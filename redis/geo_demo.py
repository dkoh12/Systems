import redis

def main():
    # Connect to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
    except redis.ConnectionError:
        print("Error: Could not connect to Redis. Make sure Redis server is running.")
        return

    geo_key = 'cities_locations'
    
    # Clear existing key for demo purposes
    r.delete(geo_key)

    print(f"--- Adding cities to {geo_key} ---")
    # Add cities with (longitude, latitude, member_name)
    # Note: Redis uses Longitude, Latitude order (x, y)
    cities = [
        (-122.4194, 37.7749, 'San Francisco'),
        (-118.2437, 34.0522, 'Los Angeles'),
        (-74.0060, 40.7128, 'New York'),
        (-0.1276, 51.5074, 'London'),
        (2.3522, 48.8566, 'Paris'),
        (139.6917, 35.6895, 'Tokyo')
    ]
    
    # geoadd takes arguments as: name, longitude, latitude, name, longitude, latitude...
    # or a list of tuples in newer redis-py versions, but let's be explicit or use the mapping
    # redis-py 3.0+ supports mapping {name: (lon, lat)} or passing values.
    # Let's use the unpacking method for clarity with the library
    for lon, lat, name in cities:
        r.geoadd(geo_key, (lon, lat, name))
        print(f"Added {name} at {lon}, {lat}")

    print("\n--- Calculating Distance ---")
    # Calculate distance between San Francisco and Los Angeles
    dist = r.geodist(geo_key, 'San Francisco', 'Los Angeles', unit='km')
    print(f"Distance between San Francisco and Los Angeles: {dist:.2f} km")

    dist_ny_london = r.geodist(geo_key, 'New York', 'London', unit='km')
    print(f"Distance between New York and London: {dist_ny_london:.2f} km")

    print("\n--- Proximity Search (Radius from Coordinate) ---")
    # Find cities within 1000km of a point near San Jose (-121.88, 37.33)
    # This should find San Francisco and Los Angeles
    search_lon, search_lat = -121.88, 37.33
    radius = 600 # km
    print(f"Searching for cities within {radius}km of ({search_lon}, {search_lat})...")
    
    # georadius is deprecated in favor of geosearch in newer Redis versions, 
    # but georadius is still widely supported. 
    # Let's use geosearch if available (Redis 6.2+), falling back to georadius logic if needed.
    # redis-py's geosearch: name, longitude, latitude, radius, unit
    
    try:
        # Using geosearch (requires Redis 6.2+)
        # We want to find members within a radius
        results = r.geosearch(
            name=geo_key,
            longitude=search_lon,
            latitude=search_lat,
            radius=radius,
            unit='km',
            withdist=True,
            sort='ASC' # Sort by distance
        )
        
        for city, dist in results:
            print(f"- {city.decode('utf-8')}: {dist:.2f} km away")
            
    except redis.ResponseError as e:
        print(f"GEOSEARCH failed (might be older Redis version): {e}")
        # Fallback to georadius
        results = r.georadius(geo_key, search_lon, search_lat, radius, unit='km', withdist=True, sort='ASC')
        for city, dist in results:
            print(f"- {city.decode('utf-8')}: {dist:.2f} km away")

    print("\n--- Proximity Search (Radius from Member) ---")
    # Find cities within 500km of Paris
    target_city = 'Paris'
    radius = 500
    print(f"Searching for cities within {radius}km of {target_city}...")
    
    results = r.geosearch(
        name=geo_key,
        member=target_city,
        radius=radius,
        unit='km',
        withdist=True,
        sort='ASC'
    )
    
    for city, dist in results:
        # Filter out the city itself if desired, though Redis returns it (distance 0)
        city_name = city.decode('utf-8')
        print(f"- {city_name}: {dist:.2f} km away")

if __name__ == "__main__":
    main()
