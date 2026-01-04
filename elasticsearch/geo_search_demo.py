import time
from elasticsearch import Elasticsearch

# Connect to local Elasticsearch
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "places"

def setup_index():
    """
    Creates an index with a geo_point field.
    """
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    
    settings = {
        "mappings": {
            "properties": {
                "name": { "type": "text" },
                "location": { "type": "geo_point" } # Latitude/Longitude
            }
        }
    }
    
    # for geo_point, we're using BKD tree index (kind of like R-tree)
    es.indices.create(index=INDEX_NAME, body=settings)
    print(f"Index '{INDEX_NAME}' created with geo_point field.")

def index_data():
    """
    Indexes places with lat/lon.
    """
    docs = [
        {
            "name": "Central Park, NY",
            "location": {"lat": 40.785091, "lon": -73.968285}
        },
        {
            "name": "Times Square, NY",
            "location": {"lat": 40.758896, "lon": -73.985130}
        },
        {
            "name": "Statue of Liberty, NY",
            "location": {"lat": 40.689247, "lon": -74.044502}
        },
        {
            "name": "Eiffel Tower, Paris",
            "location": {"lat": 48.8584, "lon": 2.2945}
        }
    ]
    
    for i, doc in enumerate(docs):
        es.index(index=INDEX_NAME, id=i+1, document=doc)
    
    es.indices.refresh(index=INDEX_NAME)
    print(f"Indexed {len(docs)} places.")

def geo_search_demo():
    print("\n--- 1. Geo Distance Query ---")
    # Find places within 5km of Times Square (40.758896, -73.985130)
    # Should find Times Square and Central Park, maybe Statue of Liberty depending on distance.
    
    center_lat = 40.758896
    center_lon = -73.985130
    distance = "5km"
    
    print(f"Searching for places within {distance} of Times Square...")
    
    query = {
        "query": {
            "bool": {
                "must": {
                    "match_all": {}
                },
                "filter": {
                    "geo_distance": {
                        "distance": distance,
                        "location": {
                            "lat": center_lat,
                            "lon": center_lon
                        }
                    }
                }
            }
        },
        "sort": [
            {
                "_geo_distance": {
                    "location": {
                        "lat": center_lat,
                        "lon": center_lon
                    },
                    "order": "asc",
                    "unit": "km"
                }
            }
        ]
    }
    
    res = es.search(index=INDEX_NAME, body=query)
    
    for hit in res['hits']['hits']:
        name = hit['_source']['name']
        dist = hit['sort'][0]
        print(f" - {name} ({dist:.2f} km away)")

    print("\n--- 2. Geo Bounding Box Query ---")
    # Define a box that covers roughly New York City, excluding Paris
    query = {
        "query": {
            "geo_bounding_box": {
                "location": {
                    "top_left": {
                        "lat": 41.0,
                        "lon": -74.5
                    },
                    "bottom_right": {
                        "lat": 40.5,
                        "lon": -73.5
                    }
                }
            }
        }
    }
    
    res = es.search(index=INDEX_NAME, body=query)
    print(f"Places in NYC Bounding Box: {res['hits']['total']['value']}")
    for hit in res['hits']['hits']:
        print(f" - {hit['_source']['name']}")

if __name__ == "__main__":
    try:
        if not es.ping():
            print("Error: Could not connect to Elasticsearch.")
        else:
            setup_index()
            index_data()
            geo_search_demo()
    except Exception as e:
        print(f"An error occurred: {e}")
