from confluent_kafka import Producer
import socket
import time
import json

def delivery_callback(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err:
        print(f'%% Message failed delivery: {err}')
    else:
        print(f'%% Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}')

def main():
    # Configuration for the Producer
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': socket.gethostname()
    }

    # Create Producer instance
    producer = Producer(conf)
    topic = 'test_topic'

    print(f"Producing messages to topic '{topic}'. Press Ctrl+C to stop.")

    try:
        i = 0
        while True:
            # Create a dictionary to represent our data
            data = {
                'id': i,
                'message': f'Hello Kafka {i}',
                'timestamp': time.time()
            }
            
            # Convert to JSON string
            value = json.dumps(data)
            
            # Produce message
            # We use the key to ensure ordering for specific keys if needed (optional)
            # Using mod 10 to ensure we hit all 3 partitions (keys '7' and '9' hit partition 0)
            key = str(i % 10) 
            
            producer.produce(topic, key=key, value=value, callback=delivery_callback)
            
            # Serve delivery callback events from previous produce() calls
            producer.poll(0)
            
            print(f"Sent: {value}")
            
            time.sleep(1) # Slow down to make it easier to follow
            i += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        producer.flush()

if __name__ == '__main__':
    main()
