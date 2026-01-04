from elasticsearch import Elasticsearch

def main():
    es = Elasticsearch("http://localhost:9200")

    # --- Method 1: The "Lazy" Way (Dynamic Mapping) ---
    # You don't need to define ANYTHING. Just index a document.
    # Elasticsearch guesses the schema (Integer, Text, Date) automatically.
    
    index_name_lazy = "lazy_index"
    if es.indices.exists(index=index_name_lazy):
        es.indices.delete(index=index_name_lazy)

    print(f"--- Method 1: Dynamic Mapping ('{index_name_lazy}') ---")
    print("Indexing a document into a non-existent index...")
    es.index(index=index_name_lazy, document={
        "username": "davidkoh",          # ES guesses "text"
        "age": 30,                       # ES guesses "long"
        "is_admin": True,                # ES guesses "boolean"
        "created_at": "2024-01-01"       # ES guesses "date"
    })
    
    # Let's see what schema ES created for us
    mapping = es.indices.get_mapping(index=index_name_lazy)
    print("Auto-generated Schema:")
    print(mapping[index_name_lazy]['mappings']['properties'])


    # --- Method 2: The "Control Freak" Way (Explicit Mapping) ---
    # You use JSON to define exact types (e.g., "keyword" vs "text").
    # This is what you do in production to optimize performance.
    
    index_name_strict = "strict_index"
    if es.indices.exists(index=index_name_strict):
        es.indices.delete(index=index_name_strict)

    print(f"\n--- Method 2: Explicit Mapping ('{index_name_strict}') ---")
    print("Defining exact schema with JSON...")
    es.indices.create(index=index_name_strict, body={
        "mappings": {
            "properties": {
                "username": { "type": "keyword" },  # Exact match only!
                "age":      { "type": "byte" },     # Save space (tinyint)
                "email":    { "type": "text" }      # Full-text search
            }
        }
    })
    
    mapping = es.indices.get_mapping(index=index_name_strict)
    print("Manually defined Schema:")
    print(mapping[index_name_strict]['mappings']['properties'])

if __name__ == "__main__":
    main()
