# Redis Exploration

This project contains Python scripts to demonstrate various Redis use cases.

## Prerequisites

1.  **Redis Server**: Ensure you have a Redis server running locally on the default port (6379).
    *   **Option A (Local Install)**:
        *   Install: `brew install redis` (on macOS)
        *   Start in background: `redis-server --daemonize yes`
        *   Stop: `redis-cli shutdown`
    *   **Option B (Docker)**:
        *   Run: `docker run --name redis-demo -p 6379:6379 -d redis`

2.  **Python Environment**:
    *   Create a virtual environment: `python3 -m venv .venv`
    *   Activate it: `source .venv/bin/activate`
    *   Install dependencies: `pip install redis`

## Scripts

### 1. Pub/Sub Demo (`pubsub_demo.py`)

Demonstrates the Publish/Subscribe messaging pattern.
- A subscriber listens to a channel.
- A publisher sends messages to that channel.

Run with:
```bash
python pubsub_demo.py
```

### 2. Sorted Set Demo (`sorted_set_demo.py`)

Demonstrates Redis Sorted Sets (ZSET) using a game leaderboard example.
- Adds players with scores.
- Retrieves the leaderboard sorted by score.
- Updates scores.
- Queries by rank and score range.

Run with:
```bash
python sorted_set_demo.py
```

### 3. Lua Script Demo (`lua_script_demo.py`)

Demonstrates using Lua scripts for atomic transactions.
- Implements an atomic money transfer between two accounts.
- Checks balance and transfers only if sufficient funds exist.
- Shows how to register and execute Lua scripts from Python.

Run with:
```bash
python lua_script_demo.py
```

### 4. Geospatial Demo (`geo_demo.py`)

Demonstrates Redis Geospatial capabilities.
- Adds cities with latitude and longitude.
- Calculates distances between cities.
- Performs proximity searches (finding cities within a radius).

Run with:
```bash
python geo_demo.py
```

### 5. Streams vs Pub/Sub (`stream_vs_pubsub.py`)

Demonstrates the key difference between Redis Streams and Pub/Sub.
- **Pub/Sub**: Shows that messages sent before a subscriber joins are lost (Fire-and-Forget).
- **Streams**: Shows that messages are stored in a log and can be read later (Persistence).

Run with:
```bash
python stream_vs_pubsub.py
```

### 6. Transactions Demo (`transaction_demo.py`)

Demonstrates Redis Transactions and Optimistic Locking.
- **Simple Transaction**: Uses `MULTI`/`EXEC` to run multiple commands atomically.
- **Optimistic Locking**: Uses `WATCH` to handle race conditions (retrying if a value changes while processing).

Run with:
```bash
python transaction_demo.py
```

## Resources

*   [Redis Commands Documentation](https://redis.io/commands) - Official reference for all Redis commands.

## Using Redis CLI

You can also interact with Redis directly using the command line interface.

1.  Start the CLI:
    ```bash
    redis-cli
    ```

2.  Try some commands corresponding to the demos:

    *   **Sorted Sets**:
        ```redis
        ZADD game_leaderboard 100 Alice 85 Bob
        ZRANGE game_leaderboard 0 -1 WITHSCORES
        ```

    *   **Pub/Sub** (Requires two terminal windows):
        *   Window 1: `SUBSCRIBE test_channel`
        *   Window 2: `PUBLISH test_channel "Hello from CLI"`

    *   **Geospatial**:
        ```redis
        GEOADD cities_locations -122.4194 37.7749 "San Francisco"
        GEODIST cities_locations "San Francisco" "Los Angeles" km
        ```


The key difference is **Persistence** vs. **Fire-and-Forget**.

I've looked at your stream_vs_pubsub.py file, and it demonstrates this perfectly:

### 1. Redis Pub/Sub (Fire-and-Forget)
*   **Like a Radio Broadcast:** If you aren't listening *right now*, you miss the message forever.
*   **No History:** Messages are not stored. If a subscriber crashes and restarts, it loses everything sent while it was down.
*   **Fan-out:** Good for sending the same notification to many active clients at once (e.g., "User X is typing...").
*   **In your code:** You published "Hello PubSub" *before* subscribing, so the subscriber received **nothing**.

### 2. Redis Streams (Persistent Log)
*   **Like a WhatsApp Group Chat:** Messages are stored in a log. You can read them now, later, or replay old messages from days ago.
*   **Consumer Groups:** Multiple workers can share the load. If you have 100 messages and 2 consumers in a group, each processes 50. (Pub/Sub sends all 100 to both).
*   **Reliability:** Supports "Acknowledgements" (ACK). If a worker crashes while processing a message, the message stays "pending" so another worker can pick it up.
*   **In your code:** You added "Temperature=20" to the stream. Even though no one was reading, the data stayed there. A consumer could come along 10 minutes later and read it.

### Summary Table

| Feature | Pub/Sub | Streams |
| :--- | :--- | :--- |
| **Storage** | None (Ephemeral) | Persistent (Append-only log) |
| **Delivery** | At-most-once (Fire & Forget) | At-least-once (Guaranteed) |
| **History** | No | Yes (Time-travel capable) |
| **Load Balancing** | No (All subs get all msgs) | Yes (Consumer Groups) |
| **Use Case** | Real-time notifications, Chat | Job queues, Event sourcing, Audit logs |