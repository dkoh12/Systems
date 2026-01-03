from confluent_kafka import Producer
import socket

def delivery_callback(err, msg):
    if not err:
        print(f"Key: {msg.key().decode('utf-8')} -> Partition: {msg.partition()}")

conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
producer = Producer(conf)
topic = 'test_topic'

# Try a larger range to find one for partition 0
for i in range(10):
    k = str(i)
    producer.produce(topic, key=k, value="test", callback=delivery_callback)

producer.flush()