import json
import sys
import random
from kazoo.client import KazooClient

CONFIG_PATH = "/my_app/config"

def main():
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()

    # Generate some random config
    new_config = {
        "db_url": f"postgres://db-{random.randint(1, 9)}.example.com:5432",
        "max_retries": random.randint(1, 5),
        "feature_flags": {
            "new_ui": random.choice([True, False])
        }
    }

    data_bytes = json.dumps(new_config).encode("utf-8")

    if zk.exists(CONFIG_PATH):
        print(f"Updating {CONFIG_PATH}...")
        zk.set(CONFIG_PATH, data_bytes)
    else:
        print(f"Creating {CONFIG_PATH}...")
        zk.create(CONFIG_PATH, data_bytes, makepath=True)

    print("Config updated successfully.")
    print(json.dumps(new_config, indent=2))
    
    zk.stop()

if __name__ == "__main__":
    main()
