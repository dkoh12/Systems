import time
from elasticsearch import Elasticsearch

# Connect to local Elasticsearch
# Assuming running on localhost:9200 with no security (xpack.security.enabled=false)
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "blog_posts"

def setup_index():
    """
    Creates an index with specific settings for text analysis.
    We define an 'english' analyzer to handle stemming (e.g., 'running' -> 'run').
    """
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    
    settings = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "english"  # Handles stemming, stopwords
                },
                "content": {
                    "type": "text",
                    "analyzer": "standard" # Standard tokenization
                },
                "category": {
                    "type": "keyword"      # Exact match only (no tokenization)
                },
                "published_date": {
                    "type": "date"
                }
            }
        }
    }
    
    es.indices.create(index=INDEX_NAME, body=settings)
    print(f"Index '{INDEX_NAME}' created.")

def index_data():
    """Indexes sample documents."""
    docs = [
        {
            "title": "Getting Started with Python",
            "content": "Python is a versatile programming language. It is great for data science.",
            "category": "Programming",
            "published_date": "2023-01-15"
        },
        {
            "title": "Advanced Python Techniques",
            "content": "Learn about decorators, generators, and context managers in Python.",
            "category": "Programming",
            "published_date": "2023-02-20"
        },
        {
            "title": "Introduction to Elasticsearch",
            "content": "Elasticsearch is a distributed, RESTful search and analytics engine.",
            "category": "Search Engines",
            "published_date": "2023-03-10"
        },
        {
            "title": "Healthy Eating Habits",
            "content": "Eating vegetables and fruits is good for your health. Avoid processed foods.",
            "category": "Health",
            "published_date": "2023-04-05"
        }
    ]
    
    for i, doc in enumerate(docs):
        es.index(index=INDEX_NAME, id=i+1, document=doc)
    
    # Refresh to make documents available for search immediately
    es.indices.refresh(index=INDEX_NAME)
    print(f"Indexed {len(docs)} documents.")

def search_demo():
    print("\n--- 1. Basic Match Query (Inverted Index) ---")
    # Searching for 'program' should match 'Programming' due to stemming in the 'english' analyzer
    query = {
        "query": {
            "match": {
                "title": "program" 
            }
        }
    }
    res = es.search(index=INDEX_NAME, body=query)
    print(f"Search for 'program' in title (Expect matches due to stemming): Found {res['hits']['total']['value']}")
    for hit in res['hits']['hits']:
        print(f" - {hit['_source']['title']}")

    print("\n--- 2. Exact Match (Keyword Field) ---")
    # Keyword fields are not analyzed. 'Programming' matches, 'programming' (lowercase) would not.
    query = {
        "query": {
            "term": {
                "category": "Programming"
            }
        }
    }
    res = es.search(index=INDEX_NAME, body=query)
    print(f"Filter by Category='Programming': Found {res['hits']['total']['value']}")
    for hit in res['hits']['hits']:
        print(f" - {hit['_source']['title']}")

    print("\n--- 3. Boolean Query (Compound) ---")
    # Must match 'python' AND must NOT match 'advanced'
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"content": "python"}}
                ],
                "must_not": [
                    {"match": {"title": "advanced"}}
                ]
            }
        }
    }
    res = es.search(index=INDEX_NAME, body=query)
    print(f"Boolean (Content='python' AND Title!='advanced'): Found {res['hits']['total']['value']}")
    for hit in res['hits']['hits']:
        print(f" - {hit['_source']['title']}")

if __name__ == "__main__":
    try:
        if not es.ping():
            print("Error: Could not connect to Elasticsearch. Make sure it is running on localhost:9200.")
        else:
            setup_index()
            index_data()
            search_demo()
    except Exception as e:
        print(f"An error occurred: {e}")
