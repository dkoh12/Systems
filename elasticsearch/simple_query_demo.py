from elasticsearch import Elasticsearch
import warnings

# Suppress warnings about "technical preview" features if any
warnings.filterwarnings("ignore")

def main():
    es = Elasticsearch("http://localhost:9200")
    
    print("--- 1. SQL Style (Like MySQL/Postgres) ---")
    # Yes! Elasticsearch speaks SQL.
    # It translates SQL into the JSON DSL automatically.
    try:
        resp = es.sql.query(body={
            "query": "SELECT name, price, category FROM products WHERE price > 500 ORDER BY price DESC"
        })
        
        # Print headers
        columns = [c['name'] for c in resp['columns']]
        print(f"{columns}")
        
        # Print rows
        for row in resp['rows']:
            print(row)
            
    except Exception as e:
        print(f"SQL Query failed: {e}")

    print("\n--- 2. ES|QL (The New 'Piped' Language) ---")
    # Introduced in ES 8.11. It looks like Splunk or Unix pipes.
    # FROM index | WHERE condition | STATS ...
    try:
        resp = es.esql.query(body={
            "query": """
                FROM products 
                | WHERE price > 100 
                | STATS avg_price = AVG(price) BY category
                | SORT avg_price DESC
            """
        })
        
        # ES|QL returns columns and values
        # Let's inspect the columns to be sure of the order
        col_names = [c['name'] for c in resp['columns']]
        print(f"Columns: {col_names}")
        
        for row in resp['values']:
            print(row)
            
    except Exception as e:
        print(f"ES|QL failed: {e}")

    print("\n--- 3. Simple Query String (URI Search) ---")
    # The "Google-style" search bar syntax.
    # You pass it as a simple string parameter 'q'.
    # Syntax: field:value AND field:value
    resp = es.search(index="products", q="category:electronics AND price:>500")
    
    print("Found expensive electronics:")
    for hit in resp['hits']['hits']:
        print(f"- {hit['_source']['name']} (${hit['_source']['price']})")

if __name__ == "__main__":
    main()
