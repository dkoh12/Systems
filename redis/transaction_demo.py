import redis
import time
import threading

def main():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
    except redis.ConnectionError:
        print("Error: Could not connect to Redis.")
        return

    key = 'account:balance'
    r.set(key, 100)
    print(f"Initial balance: {r.get(key).decode('utf-8')}")

    # --- 1. Simple Transaction (MULTI/EXEC) ---
    print("\n--- 1. Simple Transaction ---")
    print("Queuing commands: INCRBY 50, INCRBY 20")
    
    # pipeline(transaction=True) wraps commands in MULTI ... EXEC
    # This ensures all commands are executed atomically.
    pipe = r.pipeline(transaction=True)
    pipe.incrby(key, 50)
    pipe.incrby(key, 20)
    
    # Nothing happens on the server yet
    print("Executing transaction...")
    results = pipe.execute()
    
    print(f"Results: {results}") # Should be [150, 170]
    print(f"New balance: {r.get(key).decode('utf-8')}")

    # --- 2. Optimistic Locking with WATCH ---
    print("\n--- 2. Optimistic Locking (WATCH) ---")
    # Scenario: We want to double the balance, but only if it hasn't changed
    # since we read it. This prevents "lost updates".
    
    r.set(key, 10) # Reset for demo
    print(f"Reset balance to: {r.get(key).decode('utf-8')}")

    def interferer():
        """Simulates another client changing the value."""
        time.sleep(0.5)
        r2 = redis.Redis(host='localhost', port=6379, db=0)
        r2.incrby(key, 5)
        print(f"\n[Interferer] Changed balance to {r2.get(key).decode('utf-8')}")

    # Start interferer thread to simulate a race condition
    threading.Thread(target=interferer).start()

    print("Starting transaction with WATCH...")
    
    # Standard pattern for optimistic locking in redis-py
    with r.pipeline() as pipe:
        while True:
            try:
                # WATCH the key
                # If this key is modified by another client after this call
                # but before .execute(), the transaction will fail.
                pipe.watch(key)
                
                # Read current value (immediate execution because we haven't called multi() yet)
                current_val = int(pipe.get(key))
                print(f"[Main] Read balance: {current_val}")
                
                # Simulate some processing time (allowing interferer to run)
                print("[Main] Thinking (simulating work)...")
                time.sleep(1)
                
                # Start transaction block (MULTI)
                pipe.multi()
                pipe.set(key, current_val * 2)
                
                # Execute (EXEC)
                print("[Main] Attempting EXEC...")
                pipe.execute()
                
                print("[Main] Transaction successful!")
                break
            except redis.WatchError:
                print("[Main] WatchError! Value changed by someone else. Retrying...")
                # The loop will restart, watch the key again, read the NEW value, and try again.
                continue

    print(f"Final balance: {r.get(key).decode('utf-8')}")

if __name__ == "__main__":
    main()
