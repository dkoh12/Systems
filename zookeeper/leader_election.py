import time
import sys
import os
from kazoo.client import KazooClient
from kazoo.recipe.election import Election

def leader_func():
    """This function runs only when this process becomes the leader."""
    print(f"[{os.getpid()}] I AM THE LEADER! Doing critical work...")
    for i in range(10):
        print(f"[{os.getpid()}] Leader working... {i+1}/10")
        time.sleep(1)
    print(f"[{os.getpid()}] Leader retiring.")

def main():
    # Connect to Zookeeper
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()

    print(f"[{os.getpid()}] Connected to ZK. Joining election for 'my-service'...")

    # Create an Election object
    # This creates an ephemeral sequential node under /election/my-service
    election = zk.Election("/election/my-service", "my-identifier")

    # Run the election
    # This blocks until we win the election.
    # Once we win, it executes leader_func().
    # If we lose connection or leader_func finishes, we stop being leader.
    election.run(leader_func)

    print(f"[{os.getpid()}] No longer leader (or finished). Bye!")
    zk.stop()

if __name__ == "__main__":
    main()
