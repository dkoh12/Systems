# Apache Flink Demo

Apache Flink is a framework for stateful computations over unbounded and bounded data streams.

## Prerequisites

1.  **Apache Flink**: Installed via Homebrew (`brew install apache-flink`).
2.  **Java**: Required to run Flink (installed automatically by brew).

## 1. Start the Local Flink Cluster

Flink runs as a cluster (JobManager + TaskManagers). You can start a local mini-cluster:

```bash
# Start the cluster
/opt/homebrew/opt/apache-flink/libexec/bin/start-cluster.sh
```

*   **Web UI**: Once started, access the dashboard at [http://localhost:8081](http://localhost:8081).

## 2. Python Code Examples (PyFlink)

I have included two Python scripts to demonstrate Flink logic. 

> **Note:** PyFlink currently supports Python 3.8 - 3.11. If you are running Python 3.14 (as in the root `.venv`), you may need to create a separate environment with an older Python version to run these scripts directly.

### A. `simple_demo.py` (Batch-like)
Processes a static list of sentences and counts words.
```bash
python simple_demo.py
```

### B. `socket_demo.py` (Streaming)
Listens to a network socket (like the Java example).
1. Start `nc -l 9000` in one terminal.
2. Run `python socket_demo.py` in another.
3. Type in the netcat terminal to see results.

## 3. Run the Java Example (Built-in)

If you cannot run the Python scripts due to version constraints, you can run the built-in Java example:

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
