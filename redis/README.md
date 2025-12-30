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
