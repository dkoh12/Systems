import time
from elasticsearch import Elasticsearch

# Connect to local Elasticsearch
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "image_vectors"

def setup_index():
    """
    Creates an index with a dense_vector field.
    """
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    
    settings = {
        "mappings": {
            "properties": {
                "image_name": { "type": "text" },
                "description": { "type": "text" },
                "image_vector": {
                    "type": "dense_vector",
                    "dims": 3,           # 3-dimensional vector for simplicity
                    "index": True,       # Enable HNSW indexing for fast kNN
                    "similarity": "cosine" # Use cosine similarity
                }
            }
        }
    }
    
    es.indices.create(index=INDEX_NAME, body=settings)
    print(f"Index '{INDEX_NAME}' created with dense_vector field.")

def index_data():
    """
    Indexes documents with simulated vectors.
    Imagine these vectors represent color features extracted from images.
    X-axis: Redness, Y-axis: Blueness, Z-axis: Greenness
    """
    docs = [
        {
            "image_name": "Red Apple",
            "description": "A bright red apple",
            "image_vector": [0.9, 0.05, 0.05] # High Red
        },
        {
            "image_name": "Fire Truck",
            "description": "A red fire truck",
            "image_vector": [0.95, 0.02, 0.03] # Very High Red
        },
        {
            "image_name": "Blueberry",
            "description": "A blue berry",
            "image_vector": [0.05, 0.9, 0.05] # High Blue
        },
        {
            "image_name": "Leaf",
            "description": "A green leaf",
            "image_vector": [0.05, 0.05, 0.9] # High Green
        },
        {
            "image_name": "Purple Grape",
            "description": "A purple grape (Red + Blue)",
            "image_vector": [0.5, 0.5, 0.0] # Mix of Red and Blue
        }
    ]
    
    for i, doc in enumerate(docs):
        es.index(index=INDEX_NAME, id=i+1, document=doc)
    
    es.indices.refresh(index=INDEX_NAME)
    print(f"Indexed {len(docs)} vector documents.")

def vector_search_demo():
    print("\n--- kNN Vector Search ---")
    
    # Search Vector: Pure Red [1.0, 0.0, 0.0]
    # We expect 'Fire Truck' and 'Red Apple' to be closest.
    query_vector = [1.0, 0.0, 0.0]
    
    print(f"Searching for vector closest to: {query_vector} (Pure Red)")
    
    # kNN search query
    query = {
        "knn": {
            "field": "image_vector",
            "query_vector": query_vector,
            "k": 3, # Return top 3 nearest neighbors
            "num_candidates": 10
        },
        "_source": ["image_name", "description"]
    }
    
    res = es.search(index=INDEX_NAME, body=query)
    
    for hit in res['hits']['hits']:
        score = hit['_score']
        name = hit['_source']['image_name']
        print(f" - Score: {score:.4f} | {name}")

if __name__ == "__main__":
    try:
        if not es.ping():
            print("Error: Could not connect to Elasticsearch.")
        else:
            setup_index()
            index_data()
            vector_search_demo()
    except Exception as e:
        print(f"An error occurred: {e}")
