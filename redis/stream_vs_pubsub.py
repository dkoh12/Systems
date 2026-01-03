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
KEYS *

TYPE sensor_events

XINFO STREAM sensor_events
// see how many messages are in my stream.

XRANGE sensor_events - + 
// list actual messages inside stream (like SELECT *)
// - means "start from beginning"
// + means "go to end"
// can limit it by XRANGE <stream_key> - + COUNT 10

Channels are not in Redis Keys
Pub/Sub channels disappear the instant the last subscriber disconnects

XADD sensor_events * sensor B temp 24
XADD sensor_events * rider Castilla speed 30.2 position 1 location_id 1
// add an entry to my stream
// my stream doesn't need a specific schema format
// the second argument is an entry ID that identifier every entry inside a stream
// However we use "*" because we want the server to generate a new ID for us
// every new ID will be monotonically increasing

XLEN sensor_events
// returns number of items inside a stream

Entry IDs is composed of two parts
<millisecondsTime>-<seqNumber>
- millisecondsTime is local time in local Redis node generating stream ID

reason we add time in key is that redis streams support range queries by ID. 
Because ID is related to time, this gives us the ability to query time ranges for free.

we could use Redis stream as a time series store. 

To query stream by range, we're only required to specify two IDs, start and end
XRANGE sensor_events - +
XREVRANGE sensor_events + -

XREAD COUNT 2 STREAMS sensor_events 0
// listen for new items in stream sensor_events having an ID greater than 0-0

XREAD BLOCK 0 STREAMS sensor_events $
// turn it into a blocking command with timeout of 0 milliseconds (never timeout)
// $ means XREAD should use last ID as maximum ID already stored in my stream
// that way we only receive new messages starting from the time we started lsitening.
// this is similar to 'tail -f' Unix command



streams are implemented as radix trees. (compressed trie)
insert to a stream is O(1)
accessing any entry is O(n) where n is length of ID.
since stream IDs are short and of fixed length, this is usually constant time

radix tree = space optimized trie.
in plain trie, each edge stores a single symbol. one node per char.
This creates tall, sparse trees. Lots of nodes with only child

radix tree (compressed trie)
path compression: any node with any single child is merged with its child
edge is labeled with a string (sequence of char/bits) instead of just one char
so "can" and "candle" share a single edge like "can"
This reduces height of tree, number of nodes, and memory usage.

streams (like log of events keyed by ID or prefix) are often implemented on top of 
radix trees
because they're good for ordered, prefix-structured keys with fast lookups and 
range scans.

"""


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


"""
pub/sub is great for broadcast and fire + forget.
Good for real-time notifications, chat

streams (persistent append-only log)
good for job queues, event sourcing, audit logs.
"""