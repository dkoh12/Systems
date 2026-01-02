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

    # --- 1. Pub/Sub: Fire and Forget ---
    print("--- Pub/Sub Demo (Fire and Forget) ---")
    channel = 'notifications'
    
    print(f"Publishing 'Hello PubSub' to channel '{channel}'...")
    # No subscribers yet, so this message disappears into the void
    # publish returns the number of clients that received the message
    subscribers = r.publish(channel, 'Hello PubSub')
    print(f"Message published. Subscribers receiving it: {subscribers}")
    
    # Now if we subscribe, we won't see that past message
    p = r.pubsub()
    p.subscribe(channel)
    print("Subscribed now. Checking for messages...")
    
    # get_message() reads the next message. 
    # The first message is always the subscription confirmation.
    p.get_message(timeout=0.1) 
    
    # Try to get actual data
    msg = p.get_message(timeout=1.0)
    if msg and msg['type'] == 'message':
        print(f"Received: {msg['data']}")
    else:
        print("No messages received (as expected, the previous one is gone).")


    # --- 2. Streams: Persistent Log ---
    print("\n--- Streams Demo (Persistent Log) ---")
    stream_key = 'sensor_events'
    
    # Clear stream for demo
    r.delete(stream_key)
    
    print(f"Adding event 'Temperature=20' to stream '{stream_key}'...")
    # Add to stream. No consumers are reading yet.
    # XADD key * field value
    # '*' means let Redis generate the ID (timestamp-sequence)
    event_id1 = r.xadd(stream_key, {'sensor': 'A', 'temp': 20})
    print(f"Event stored with ID: {event_id1.decode('utf-8')}")
    
    print(f"Adding event 'Temperature=22' to stream '{stream_key}'...")
    event_id2 = r.xadd(stream_key, {'sensor': 'A', 'temp': 22})
    print(f"Event stored with ID: {event_id2.decode('utf-8')}")

    print("\nReading from stream (starting from beginning)...")
    # XREAD streams={key: start_id}
    # '0-0' means start from the very beginning
    # count=10 limits results to 10 items
    events = r.xread({stream_key: '0-0'}, count=10)
    
    # Format of events: [[stream_name, [[id, {data}], [id, {data}]]]]
    for stream, message_list in events:
        for msg_id, msg_data in message_list:
            # Decode binary data for display
            decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in msg_data.items()}
            print(f"Read ID {msg_id.decode('utf-8')}: {decoded_data}")

    print("\nStreams preserved the data even though we weren't listening when it was sent!")

if __name__ == "__main__":
    main()


"""
Hashes (objects)
// Use HSET to store field-value pairs. Ideal for objects

HSET user:101 name “John” age 30 email “john@example.com”

Lists (ordered collections)
// use LPUSH or RPUSH to create a list by adding elements to start or end

LPUSH tasks “Email client” “Update docs”

Sets (unique collections)
// use SADD to create a set
// every member in set is unique

SADD tags:blog “redis” “database” “coding”

Sorted Set (ranked collections)
// use ZADD to create a set where each member is associated with a score for sorting

ZADD leaderboard 100 “player1” 150 “player2”

"""