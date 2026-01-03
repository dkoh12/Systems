import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    # Connection parameters
    db_params = {
        "dbname": "postgres",
        "user": "postgres",
        "password": "password",
        "host": "localhost",
        "port": "5432"
    }

    try:
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=RealDictCursor)
        print("Connected to PostgreSQL")
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return

    # TSVector = Text Search Vector
    # 1. Setup: Create table with TSVECTOR column
    print("\n--- Setting up Full Text Search Table ---")
    try:
        cur.execute("DROP TABLE IF EXISTS documents;")
        cur.execute("""
            CREATE TABLE documents (
                id SERIAL PRIMARY KEY,
                title TEXT,
                content TEXT,
                -- Generated column that automatically updates the tsvector
                -- 'english' is the configuration (stop words, stemming rules)
                search_vector TSVECTOR GENERATED ALWAYS AS (
                    setweight(to_tsvector('english', coalesce(title, '')), 'A') || 
                    setweight(to_tsvector('english', coalesce(content, '')), 'B')
                ) STORED
            );
        """)
        
        # Create a GIN index on the vector column for fast searching
        cur.execute("CREATE INDEX documents_search_idx ON documents USING GIN (search_vector);")
        print("Table 'documents' created with GIN index on TSVECTOR.")

        # 2. Insert Data
        print("\n--- Inserting Documents ---")
        docs = [
            ("PostgreSQL Tutorial", "PostgreSQL is a powerful, open source object-relational database system."),
            ("Redis Guide", "Redis is an in-memory data structure store, used as a database, cache, and message broker."),
            ("Full Text Search", "Full text search in PostgreSQL allows you to search for documents that contain specific words."),
            ("Database Indexing", "Indexes are used to speed up search queries in databases like Postgres and MySQL."),
            ("Python and SQL", "Using Python with SQL databases is common for data analysis and web development.")
        ]
        
        for title, content in docs:
            cur.execute("INSERT INTO documents (title, content) VALUES (%s, %s)", (title, content))
        print(f"Inserted {len(docs)} documents.")

        # 3. Perform Searches
        
        # Search 1: Simple word match
        query = "database"
        print(f"\n--- Search for '{query}' ---")
        # @@ is the match operator
        # plainto_tsquery parses the text and converts it to a query
        cur.execute("""
            SELECT title, content, 
                   ts_rank(search_vector, plainto_tsquery('english', %s)) as rank
            FROM documents
            WHERE search_vector @@ plainto_tsquery('english', %s)
            ORDER BY rank DESC;
        """, (query, query))
        
        for row in cur.fetchall():
            print(f"[{row['rank']:.4f}] {row['title']}")

        # Search 2: Stemming (searching for 'searching' matches 'search')
        query = "searching"
        print(f"\n--- Search for '{query}' (demonstrates stemming) ---")
        cur.execute("""
            SELECT title, content
            FROM documents
            WHERE search_vector @@ plainto_tsquery('english', %s);
        """, (query,))
        
        for row in cur.fetchall():
            print(f"- {row['title']}")

        # Search 3: Boolean operators (Postgres & SQL)
        # to_tsquery allows boolean operators like & (AND), | (OR), ! (NOT)
        query_str = "Postgres & SQL"
        print(f"\n--- Boolean Search: '{query_str}' ---")
        cur.execute("""
            SELECT title
            FROM documents
            WHERE search_vector @@ to_tsquery('english', 'Postgres & SQL');
        """)
        
        for row in cur.fetchall():
            print(f"- {row['title']}")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
