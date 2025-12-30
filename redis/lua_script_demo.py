import redis
import time

def main():
    # Connect to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
    except redis.ConnectionError:
        print("Error: Could not connect to Redis. Make sure Redis server is running.")
        return

    # --- Scenario: Atomic Money Transfer ---
    # We want to transfer money from Account A to Account B.
    # This must be atomic: we can't deduct from A and then fail to add to B.
    # Also, we must check if A has enough funds before deducting.

    account_a = 'account:A'
    account_b = 'account:B'

    # 1. Setup initial balances
    print("--- Setting up initial balances ---")
    r.set(account_a, 100)
    r.set(account_b, 50)
    print(f"Account A: {r.get(account_a).decode('utf-8')}")
    print(f"Account B: {r.get(account_b).decode('utf-8')}")

    # 2. Define the Lua script
    # KEYS[1] = sender key
    # KEYS[2] = receiver key
    # ARGV[1] = amount to transfer
    with open('transfer.lua', 'r') as f:
        lua_script = f.read()

    # 3. Register the script (optional but good practice for performance)
    transfer_script = r.register_script(lua_script)

    # 4. Execute the transfer
    amount_to_transfer = 30
    print(f"\n--- Attempting to transfer {amount_to_transfer} from A to B ---")
    
    # We can run the script object directly
    result = transfer_script(keys=[account_a, account_b], args=[amount_to_transfer])
    
    success, new_balance = result
    if success:
        print(f"Transfer successful! Account A new balance: {new_balance}")
    else:
        print(f"Transfer failed! Insufficient funds. Account A balance: {new_balance}")

    print(f"Account B new balance: {r.get(account_b).decode('utf-8')}")

    # 5. Attempt a transfer that should fail
    amount_to_transfer = 200
    print(f"\n--- Attempting to transfer {amount_to_transfer} from A to B ---")
    
    result = transfer_script(keys=[account_a, account_b], args=[amount_to_transfer])
    
    success, new_balance = result
    if success:
        print(f"Transfer successful! Account A new balance: {new_balance}")
    else:
        print(f"Transfer failed! Insufficient funds. Account A balance: {new_balance}")

    print(f"Account B balance: {r.get(account_b).decode('utf-8')}")

if __name__ == "__main__":
    main()
