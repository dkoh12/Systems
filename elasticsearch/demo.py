from elasticsearch import Elasticsearch
import time

def main():
    # Connect to Elasticsearch
    # Note: In a real production env with security enabled, you'd need ca_certs and basic_auth
    es = Elasticsearch("http://localhost:9200")

    # Wait for ES to be ready
    print("Connecting to Elasticsearch...")
    if not es.ping():
        print("Could not connect to Elasticsearch!")
        return
    print("Connected!")

    index_name = "products"

    # 1. Create an Index (like a Table)
    # We can define mappings (schema) or let ES guess.
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    
    es.indices.create(index=index_name)
    print(f"Index '{index_name}' created.")

    # 2. Index some Data (Documents)
    products = [
        {"name": "iPhone 15", "description": "Apple smartphone with A16 chip", "category": "electronics", "price": 999},
        {"name": "Samsung Galaxy S23", "description": "Android smartphone with great camera", "category": "electronics", "price": 899},
        {"name": "MacBook Pro", "description": "Apple laptop for professionals", "category": "computers", "price": 1999},
        {"name": "Dell XPS 13", "description": "Windows laptop, thin and light", "category": "computers", "price": 1299},
        {"name": "Sony Headphones", "description": "Noise cancelling headphones", "category": "electronics", "price": 299},
        {"name": "Apple", "description": "Fresh red fruit", "category": "groceries", "price": 1},
    ]

    for i, product in enumerate(products):
        es.index(index=index_name, id=i+1, document=product)
    
    print(f"Indexed {len(products)} documents.")

    # Refresh to make documents searchable immediately
    es.indices.refresh(index=index_name)

    # 3. Search!
    print("\n--- 🔍 Search: 'Apple' ---")
    # This is a "Full Text Search". It will find "Apple" in name OR description.
    # It will match "Apple" (the company) and "Apple" (the fruit).
    response = es.search(index=index_name, query={
        "multi_match": {
            "query": "Apple",
            "fields": ["name", "description"]
        }
    })

    for hit in response['hits']['hits']:
        score = hit['_score']
        source = hit['_source']
        print(f"Score: {score:.2f} | Name: {source['name']} | Category: {source['category']}")

    print("\n--- 🔍 Search: 'smartphone' (Fuzzy) ---")
    # Fuzzy search handles typos
    response = es.search(index=index_name, query={
        "match": {
            "description": {
                "query": "smartphne", # Typo!
                "fuzziness": "AUTO"
            }
        }
    })

    for hit in response['hits']['hits']:
        score = hit['_score']
        source = hit['_source']
        print(f"Score: {score:.2f} | Name: {source['name']} | Desc: {source['description']}")

if __name__ == "__main__":
    main()
