import time
import sys
import os
import logging
from kazoo.client import KazooClient
from kazoo.recipe.election import Election

# Configure logging to see Zookeeper interactions
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
# Mute the verbose kazoo logs slightly
logging.getLogger('kazoo').setLevel(logging.WARN)

def work_as_leader():
    pid = os.getpid()
    print(f"\n[Leader] I (PID {pid}) am now the LEADER! 👑")
    print("[Leader] I am coordinating the cluster...")
    
    count = 0
    while True:
        time.sleep(2)
        count += 1
        print(f"[Leader] Still leading... (Heartbeat {count})")

def main():
    # Connect to Zookeeper
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()

    pid = os.getpid()
    election_path = "/system_leader"
    
    print(f"--- Worker {pid} started ---")
    print(f"Worker {pid} is trying to join the election at {election_path}...")

    # Create an Election object
    election = zk.Election(election_path, identifier=f"Worker-{pid}")

    # This method blocks until this process wins the election
    # Once it wins, it executes the function passed to it
    election.run(work_as_leader)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping worker...")
