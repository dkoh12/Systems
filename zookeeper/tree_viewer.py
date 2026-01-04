from kazoo.client import KazooClient

def print_tree(zk, path, level=0):
    # Get children of the current node
    try:
        children = zk.get_children(path)
    except Exception:
        return

    # Print current node
    node_name = path.split('/')[-1] if path != '/' else '/'
    indent = "    " * level
    print(f"{indent}📂 {node_name}")

    # Recurse
    for child in children:
        full_path = f"{path}/{child}" if path != "/" else f"/{child}"
        print_tree(zk, full_path, level + 1)

def main():
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()
    
    print("\n--- 🌳 Current Zookeeper Hierarchy 🌳 ---")
    # We start looking at the root, but specifically our election folder
    if zk.exists("/system_leader"):
        print_tree(zk, "/system_leader")
    else:
        print("Path /system_leader does not exist yet.")
    
    zk.stop()

if __name__ == "__main__":
    main()
