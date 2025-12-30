import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    # Connection parameters - adjust as needed
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
        print("Please ensure PostgreSQL is running and the connection details are correct.")
        return

    # 1. Setup: Enable PostGIS extension and create table
    print("\n--- Setting up Geospatial Table ---")
    try:
        # Enable PostGIS (requires PostGIS installed on the server)
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        cur.execute("DROP TABLE IF EXISTS cities;")
        cur.execute("""
            CREATE TABLE cities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                location GEOMETRY(Point, 4326) -- SRID 4326 is WGS 84 (standard lat/lon)
            );
        """)
        
        # Create a spatial index (GIST)
        cur.execute("CREATE INDEX cities_location_idx ON cities USING GIST (location);")
        print("Table 'cities' created with PostGIS geometry column and GIST index.")

        # 2. Insert Data
        print("\n--- Inserting Data ---")
        cities_data = [
            ('San Francisco', -122.4194, 37.7749),
            ('Los Angeles', -118.2437, 34.0522),
            ('New York', -74.0060, 40.7128),
            ('London', -0.1276, 51.5074),
            ('Paris', 2.3522, 48.8566),
            ('San Jose', -121.8863, 37.3382)
        ]
        
        for name, lon, lat in cities_data:
            # ST_SetSRID(ST_MakePoint(lon, lat), 4326) creates a point with the correct coordinate system
            cur.execute("""
                INSERT INTO cities (name, location) 
                VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
            """, (name, lon, lat))
        print(f"Inserted {len(cities_data)} cities.")

        # 3. Proximity Search (Find cities within radius)
        print("\n--- Proximity Search: Cities within 100km of San Francisco ---")
        # San Francisco coordinates
        sf_lon, sf_lat = -122.4194, 37.7749
        
        # ST_DWithin checks if geometries are within a distance. 
        # Note: For SRID 4326 (degrees), ST_DWithin uses degrees by default. 
        # To use meters, we cast to geography: location::geography
        cur.execute("""
            SELECT name, 
                   ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) / 1000 as dist_km
            FROM cities
            WHERE ST_DWithin(
                location::geography, 
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 
                100000 -- 100km in meters
            )
            ORDER BY dist_km ASC;
        """, (sf_lon, sf_lat, sf_lon, sf_lat))
        
        results = cur.fetchall()
        for row in results:
            print(f"- {row['name']}: {row['dist_km']:.2f} km")

        # 4. K-Nearest Neighbors (KNN)
        print("\n--- KNN Search: 3 Closest cities to Paris ---")
        paris_lon, paris_lat = 2.3522, 48.8566
        
        # The <-> operator returns the distance between two geometries.
        # Used in ORDER BY, it utilizes the GIST index for efficient KNN.
        cur.execute("""
            SELECT name, 
                   ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) / 1000 as dist_km
            FROM cities
            ORDER BY location <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            LIMIT 3;
        """, (paris_lon, paris_lat, paris_lon, paris_lat))
        
        results = cur.fetchall()
        for row in results:
            print(f"- {row['name']}: {row['dist_km']:.2f} km")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
