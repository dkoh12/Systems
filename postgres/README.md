# PostgreSQL Exploration

This project demonstrates advanced PostgreSQL features: Geospatial Indexing (PostGIS) and Full Text Search.

## Prerequisites

1.  **PostgreSQL Server**: You need a running PostgreSQL instance.
    *   **Local Install**: `brew install postgresql` (macOS)
    *   **Docker**: `docker run --name postgres-demo -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgis/postgis`
        *   *Note*: For the geospatial demo, you specifically need the **PostGIS** extension installed. The standard `postgres` image doesn't include it. Use `postgis/postgis` image or install `postgis` package locally.

2.  **Python Environment**:
    *   Create venv: `python3 -m venv .venv`
    *   Activate: `source .venv/bin/activate`
    *   Install driver: `pip install psycopg2-binary`

## Configuration

The scripts assume the following default connection parameters. You may need to edit the `db_params` dictionary in the scripts if your setup differs:
*   **Host**: localhost
*   **Port**: 5432
*   **User**: postgres
*   **Password**: password
*   **Database**: postgres

## Scripts

### 1. Geospatial Demo (`geospatial_demo.py`)

Demonstrates using PostGIS for location-based queries.
*   **Setup**: Creates a table with a `GEOMETRY` column and a `GIST` index.
*   **Features**:
    *   **Proximity Search**: Finds cities within 100km of a point using `ST_DWithin`.
    *   **KNN (K-Nearest Neighbors)**: Finds the closest N items efficiently using the `<->` operator.

Run with:
```bash
python geospatial_demo.py
```

### 2. Full Text Search Demo (`fulltext_search_demo.py`)

Demonstrates PostgreSQL's built-in full text search capabilities.
*   **Setup**: Creates a table with a `TSVECTOR` column and a `GIN` index.
*   **Features**:
    *   **Stemming**: "searching" matches "search".
    *   **Ranking**: Results are ranked by relevance (`ts_rank`).
    *   **Boolean Queries**: Supports AND/OR/NOT logic.

Run with:
```bash
python fulltext_search_demo.py
```
