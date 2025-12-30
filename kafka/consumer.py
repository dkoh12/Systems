from confluent_kafka import Consumer, KafkaError, KafkaException
import sys
import json
import time

def main():
    # Configuration for the Consumer
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'python_example_group_1',
        'auto.offset.reset': 'earliest' # Start from the beginning if no offset is stored
    }

    # Create Consumer instance
    consumer = Consumer(conf)

    topic = 'test_topic'
    
    # Subscribe to topic
    consumer.subscribe([topic])
    
    print(f"Subscribed to topic '{topic}'. Waiting for messages...")

    try:
        while True:
            # Poll for new messages
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write(f'%% {msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}\n')
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print(f"Topic '{topic}' not found yet. Waiting...")
                    time.sleep(1)
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Proper message
                try:
                    # Decode the value
                    value = msg.value().decode('utf-8')
                    data = json.loads(value)
                    
                    print(f"Received message: key={msg.key().decode('utf-8') if msg.key() else None}, value={data}")
                    print(f"    Partition: {msg.partition()}, Offset: {msg.offset()}")
                except Exception as e:
                    print(f"Error processing message: {e}")

    except KeyboardInterrupt:
        print("\nStopping consumer...")
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

if __name__ == '__main__':
    main()
