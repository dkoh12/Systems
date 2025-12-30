# Elasticsearch System Demos

This folder contains examples of using Elasticsearch for different search scenarios: Full Text Search, Vector Search, and Geospatial Search.

## Prerequisites

1.  **Python Environment**:
    The virtual environment is already set up. Activate it if needed:
    ```bash
    source .venv/bin/activate
    ```

2.  **Elasticsearch Instance**:
    You need a running Elasticsearch instance. The easiest way is to run it via Docker.
    
    **Run Elasticsearch (Single Node, No Security for Dev):**
    ```bash
    docker run --name es-local -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -d docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    ```
    
    *Note: These scripts assume ES is running at `http://localhost:9200` without authentication for simplicity.*

## Demos

### 1. Full Text Search (`text_search_demo.py`)
Demonstrates the power of the **Inverted Index**.
-   Creates an index with specific analyzers (Standard vs English).
-   Indexes sample blog posts.
-   Performs:
    -   **Match Query**: Standard full-text search.
    -   **Phrase Match**: Searching for exact phrases.
    -   **Boolean Query**: Combining conditions (must, should).

### 2. Vector Search (`vector_search_demo.py`)
Demonstrates **Dense Vector** search (Semantic Search).
-   Creates an index with a `dense_vector` field mapping.
-   Indexes documents with pre-computed (simulated) embeddings.
-   Performs a **k-Nearest Neighbor (kNN)** search to find semantically similar items.

### 3. Geospatial Search (`geo_search_demo.py`)
Demonstrates **Geo-Point** indexing.
-   Creates an index with `geo_point` fields.
-   Indexes places with lat/lon coordinates.
-   Performs:
    -   **Geo Distance Query**: Find items within X km.
    -   **Geo Bounding Box**: Find items within a rectangular area.

## Running the Demos

```bash
python text_search_demo.py
python vector_search_demo.py
python geo_search_demo.py
```
