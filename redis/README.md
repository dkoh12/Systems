# Redis Exploration

This project contains Python scripts to demonstrate various Redis use cases.

## Prerequisites

1.  **Redis Server**: Ensure you have a Redis server running locally on the default port (6379).
    *   If you have Docker, you can run: `docker run --name redis-demo -p 6379:6379 -d redis`
    *   Or install it via your package manager (e.g., `brew install redis` on macOS).

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
