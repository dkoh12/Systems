import multiprocessing
import time
import sys
from confluent_kafka import Consumer, KafkaError

def run_consumer(consumer_name):
    """
    Runs a single consumer instance that joins 'demo_group'.
    """
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'demo_group',
        'auto.offset.reset': 'earliest',
        'client.id': consumer_name
    }

    # Callback to show partition assignment
    def on_assign(consumer, partitions):
        print(f"🟢 [{consumer_name}] Assigned partitions: {[p.partition for p in partitions]}")
        consumer.assign(partitions)

    def on_revoke(consumer, partitions):
        print(f"🔴 [{consumer_name}] Revoked partitions: {[p.partition for p in partitions]}")
        consumer.unassign()

    consumer = Consumer(conf)
    
    # Subscribe to the topic
    # We pass the callbacks to see the rebalancing happen in real-time
    consumer.subscribe(['test_topic'], on_assign=on_assign, on_revoke=on_revoke)
    
    print(f"[{consumer_name}] Starting...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"[{consumer_name}] Error: {msg.error()}")
                    break

            # Print which consumer got the message and from which partition
            print(f"[{consumer_name}] Received from Partition {msg.partition()}: {msg.value().decode('utf-8')}")
            
    except KeyboardInterrupt:
        pass
    finally:
        print(f"[{consumer_name}] Closing")
        consumer.close()

def main():
    print("Starting 3 consumers in 'demo_group'...")
    print("You should see partitions being distributed among them.")
    print("Press Ctrl+C to stop.")
    
    # Spawn 3 separate processes to simulate 3 different machines/services
    processes = []
    for i in range(3):
        p = multiprocessing.Process(target=run_consumer, args=(f"Consumer-{i+1}",))
        p.start()
        processes.append(p)
        # Stagger start slightly to see rebalancing happen
        time.sleep(5) 

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nStopping all consumers...")
        for p in processes:
            p.terminate()

if __name__ == '__main__':
    main()
