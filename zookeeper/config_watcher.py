import time
import json
from kazoo.client import KazooClient

CONFIG_PATH = "/my_app/config"

def main():
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()

    # Ensure the path exists
    zk.ensure_path(CONFIG_PATH)

    print(f"Watching {CONFIG_PATH} for changes...")
    print("Try updating the config in another terminal using 'python config_updater.py'")

    # @zk.DataWatch registers a function to be called whenever the node changes
    @zk.DataWatch(CONFIG_PATH)
    def watch_config(data, stat):
        if data:
            config = json.loads(data.decode("utf-8"))
            print(f"\n[EVENT] Config Updated!")
            print(f"  - Database URL: {config.get('db_url')}")
            print(f"  - Max Retries:  {config.get('max_retries')}")
            print(f"  - Version:      {stat.version}")
        else:
            print("\n[EVENT] Config node exists but is empty.")

    # Keep the script running to receive events
    while True:
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
