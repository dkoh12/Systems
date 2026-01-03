# Apache ZooKeeper Demos

This folder contains examples of using ZooKeeper for distributed coordination.

## Prerequisites

1.  **ZooKeeper Server**: Installed via Homebrew.
2.  **Python Client**: `kazoo` installed in the root `.venv`.

## 1. Start ZooKeeper Server
You need a running ZK instance.
```bash
zkServer start
```
*(To stop it later: `zkServer stop`)*

## 2. Leader Election Demo (`leader_election.py`)
This demonstrates how multiple processes compete to be the single "Leader".

1.  Open **Terminal A**:
    ```bash
    python leader_election.py
    ```
    *It will immediately become the leader.*

2.  Open **Terminal B**:
    ```bash
    python leader_election.py
    ```
    *It will block, waiting for the leader to die.*

3.  **Kill Terminal A** (Ctrl+C).
    *   Watch Terminal B immediately take over as the new leader.

## 3. Dynamic Configuration Demo (`config_watcher.py`)
This demonstrates how to push configuration updates to all running services instantly.

1.  Open **Terminal A** (The Service):
    ```bash
    python config_watcher.py
    ```
    *It sits and waits for updates.*

2.  Open **Terminal B** (The Admin):
    ```bash
    python config_updater.py
    ```
    *Run this multiple times. Every time you run it, Terminal A will print the new config instantly.*

## Key Concepts Used
*   **Ephemeral Nodes**: Used in election. If a process dies, its node disappears, triggering the election for others.
*   **Watches**: Used in config. The client asks ZK to "notify me if this node changes".
