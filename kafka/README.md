# Kafka Exploration

This project demonstrates how to use Apache Kafka with Python using the `confluent-kafka` library.

## Prerequisites

1.  **Kafka**: Ensure you have Kafka installed (e.g., via `brew install kafka`).
2.  **Python Environment**:
    *   Create a virtual environment: `python3 -m venv .venv`
    *   Activate it: `source .venv/bin/activate`
    *   Install dependencies: `pip install confluent-kafka`

## Setup Local Kafka Environment (KRaft mode)

Since Docker was not available, we are running Kafka locally in KRaft mode (no Zookeeper needed).

1.  **Configuration**: A local configuration file is created at `config/server.properties`.
2.  **Storage**: Data is stored in `data/`.

### 1. First Time Setup (Run Once)

If you are running this for the first time (or if the `data/` directory is empty), you need to format the storage:

```bash
# Generate a cluster ID
uuid=$(kafka-storage random-uuid)

# Format storage
kafka-storage format -t $uuid -c config/server.properties
```

### 2. Start Kafka Server

```bash
kafka-server-start -daemon config/server.properties
```

### 3. Verify It's Running

```bash
kafka-topics --list --bootstrap-server localhost:9092
```

## Running the Demos

Open two terminal windows.

### Terminal 1: Consumer

Start the consumer first. It will wait for the topic to be created if it doesn't exist.

```bash
cd Systems/kafka
source .venv/bin/activate
python consumer.py
```

### Terminal 2: Producer

Start the producer to send messages to the topic.

```bash
cd Systems/kafka
source .venv/bin/activate
python producer.py
```

You should see messages being sent in the producer window and appearing in the consumer window.

## Cleanup

To stop the Kafka server:
```bash
kafka-server-stop
```
