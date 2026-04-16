# Systems 🛠️

A hands-on playground for distributed systems and infrastructure tools — each folder contains runnable demos, configuration examples, and notes.

## 📁 Structure

### 🔴 [Redis](./redis/)
In-memory data store demos covering pub/sub, streams, sorted sets, geospatial queries, Lua scripting, and transactions.

### 🐘 [PostgreSQL](./postgres/)
Postgres demos including full-text search, geospatial queries with PostGIS, and tsvector indexing.

### 🔍 [Elasticsearch](./elasticsearch/)
Search engine demos covering index creation, text search, vector search, and geo search.

### 📨 [Kafka](./kafka/)
Event streaming demos including producers/consumers, consumer groups, partitions, and Kafka Connect.

### ⚡ [Flink](./Flink/)
Stream processing demos with Apache Flink — simple and socket-based pipelines.

### ⏱️ [Temporal](./Temporal/)
Workflow orchestration demos with Temporal — workers, workflows, starters, and comparisons with Flink.

### 🦁 [Zookeeper](./zookeeper/)
Distributed coordination demos — leader election, config watching, and tree viewing.

## 🐳 Docker

Each service has its own Docker setup. A root [`docker-compose.yml`](./docker-compose.yml) is provided for spinning up the full stack.

```bash
docker compose up -d
```

## 🚀 How to Use

1. Pick a technology folder
2. Read its `README.md` for setup instructions
3. Run the demo scripts with Python

---

*Built for learning and experimentation with distributed systems. 🧪*
