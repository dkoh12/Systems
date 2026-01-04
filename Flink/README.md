# Apache Flink Demo

Apache Flink is a framework for stateful computations over unbounded and bounded data streams.

## Running with Docker (Recommended)

We have set up a custom Docker environment that includes Python and PyFlink.

### 1. Start the Cluster
Make sure to build the containers to include the Python dependencies:

```bash
docker-compose up -d --build flink-jobmanager flink-taskmanager
```

*   **Web UI**: [http://localhost:8081](http://localhost:8081)

### 2. Run Python Examples

All scripts are mounted to `/opt/flink/user_code` inside the container.

#### A. `simple_demo.py` (Batch)
Processes a static list of sentences.

```bash
docker exec -it systems-flink-jm python3 /opt/flink/user_code/simple_demo.py
```

#### B. `socket_demo.py` (Streaming)
Listens to a network socket.

**Terminal 1 (Start Data Server):**
```bash
docker exec -it systems-flink-jm nc -l 9000
```

**Terminal 2 (Run Flink Job):**
```bash
# We must use the container name 'systems-flink-jm' so the TaskManager can find the netcat server
docker exec -it systems-flink-jm python3 /opt/flink/user_code/socket_demo.py systems-flink-jm 9000
```

Type words into **Terminal 1** to see the counts in **Terminal 2**.

---

## Running Locally (Mac/Linux)

If you prefer to run outside Docker, you need Java and Flink installed.

### Prerequisites
1.  **Apache Flink**: `brew install apache-flink`
2.  **Java**: (Installed by brew)
3.  **Python**: PyFlink requires Python 3.8 - 3.11. (Current system Python 3.14 is too new).

### Start Local Cluster
```bash
/opt/homebrew/opt/apache-flink/libexec/bin/start-cluster.sh
```

### Run Java Example
```bash
# Terminal 1
nc -l 9000

# Terminal 2
flink run /opt/homebrew/opt/apache-flink/libexec/examples/streaming/SocketWindowWordCount.jar --port 9000

# Terminal 3 (View Logs)
tail -f /opt/homebrew/opt/apache-flink/libexec/log/flink-*-taskexecutor-*.out
```

### Stop Cluster
```bash
/opt/homebrew/opt/apache-flink/libexec/bin/stop-cluster.sh
```

### Step A: Start a Text Stream (Terminal 1)
We use `nc` (netcat) to create a simple text server on port 9000.
```bash
nc -l 9000
```
*Type words here after starting the Flink job.*

### Step B: Submit the Flink Job (Terminal 2)
```bash
flink run /opt/homebrew/opt/apache-flink/libexec/examples/streaming/SocketWindowWordCount.jar --port 9000
```

### Step C: Watch the Output (Terminal 3)
The output is written to the TaskManager logs. To see it live:
```bash
tail -f /opt/homebrew/opt/apache-flink/libexec/log/flink-*-taskexecutor-*.out
```

## 3. Stop the Cluster
When finished:
```bash
/opt/homebrew/opt/apache-flink/libexec/bin/stop-cluster.sh
```

## Source Code Reference
The `SocketWindowWordCount` logic looks roughly like this (Java):

```java
DataStream<String> text = env.socketTextStream("localhost", port, "\n");

DataStream<WordWithCount> windowCounts = text
    .flatMap(new FlatMapFunction<String, WordWithCount>() {
        public void flatMap(String value, Collector<WordWithCount> out) {
            for (String word : value.split("\\s")) {
                out.collect(new WordWithCount(word, 1L));
            }
        }
    })
    .keyBy(value -> value.word)
    .window(TumblingProcessingTimeWindows.of(Time.seconds(5)))
    .reduce(new ReduceFunction<WordWithCount>() {
        public WordWithCount reduce(WordWithCount a, WordWithCount b) {
            return new WordWithCount(a.word, a.count + b.count);
        }
    });

windowCounts.print().setParallelism(1);
```
