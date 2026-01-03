from confluent_kafka import Producer
import socket

def delivery_callback(err, msg):
    if not err:
        print(f"Key: {msg.key().decode('utf-8')} -> Partition: {msg.partition()}")

conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
producer = Producer(conf)
topic = 'test_topic'

keys = ['0', '1', '2', '3', '4']
for k in keys:
    producer.produce(topic, key=k, value="test", callback=delivery_callback)

producer.flush()
