import redis
import threading
import time

def publisher(r, channel, n_messages):
    """Publishes messages to a channel."""
    time.sleep(1) # Give subscriber time to start
    for i in range(n_messages):
        message = f"Message {i+1}"
        print(f"Publishing: {message}")
        r.publish(channel, message)
        time.sleep(0.5)
    
    # Send a stop signal
    r.publish(channel, "STOP")

def subscriber(r, channel):
    """Subscribes to a channel and prints messages."""
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    
    print(f"Subscribed to {channel}...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data'].decode('utf-8')
            print(f"Received: {data}")
            if data == "STOP":
                print("Stopping subscriber...")
                break

def main():
    # Connect to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping() # Check connection
    except redis.ConnectionError:
        print("Error: Could not connect to Redis. Make sure Redis server is running.")
        return

    channel = 'test_channel'
    n_messages = 5

    # Create threads for publisher and subscriber
    sub_thread = threading.Thread(target=subscriber, args=(r, channel))
    pub_thread = threading.Thread(target=publisher, args=(r, channel, n_messages))

    sub_thread.start()
    pub_thread.start()

    sub_thread.join()
    pub_thread.join()
    
    print("Pub/Sub demo finished.")

if __name__ == "__main__":
    main()
