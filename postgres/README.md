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

----

since we have pgadmin installed

### How to access it
1.  Open your browser to: **[http://localhost:5050](http://localhost:5050)**
2.  **Login** with:
    *   **Email:** `admin@admin.com`
    *   **Password:** `root`

### How to connect to your Database
Once logged in, you need to add your server:
1.  Click **"Add New Server"**.
2.  **General** tab: Name it `Local Postgres`.
3.  **Connection** tab:
    *   **Host name/address:** postgres (Use the container name, not `localhost`, because pgAdmin is running inside the Docker network). (systems-postgres)
    *   **Port:** `5432`
    *   **Maintenance database:** postgres
    *   **Username:** postgres
    *   **Password:** `password`
4.  Click **Save**.

You will then see your `cities` and `documents` tables under **Schemas > public > Tables**.


----
Since your Postgres is running in a Docker container, the easiest way to access the CLI is to "exec" into the container.

### 1. How to connect
Run this command in your terminal to open the Postgres shell (`psql`):

```bash
docker exec -it systems-postgres psql -U postgres
```

### 2. Cheat Sheet for `psql` commands
Once you are inside the shell (you will see a `postgres=#` prompt), here are the most useful commands:

| Command | Description |
| :--- | :--- |
| `\l` | **List** all databases. |
| `\c dbname` | **Connect** to a specific database. |
| `\dt` | **List Tables** in the current database. |
| `\d tablename` | **Describe** a table (show columns, types, indexes). |
| `\x` | **Expanded display** (toggles on/off). Great for reading wide rows (like JSON or long text). |
| `\q` | **Quit** the shell. |

### 3. Queries to try (based on your demos)
Since you just ran the demos, you can inspect the data:

**Check the Geospatial data:**
```sql
SELECT * FROM cities;
```

**Check the Full Text Search data:**
```sql
-- You will see the 'search_vector' column is a weird looking string of lexemes
SELECT id, title, search_vector FROM documents-- You will see the 'search_vector' column is a weird looking string of lexemes
SELECT id, title, search_vector FROM documents;
```

**Run a manual SQL query:**
```sql
SELECT name, ST_AsText(location) FROM cities WHERE name = 'Paris';
```