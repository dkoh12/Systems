Elasticsearch is famous because it doesn't just use one type of index (like a B-Tree in SQL). It uses different data structures depending on the **data type** to make search instant.

We have an index for every column (every data field) in elasticsearch. 
LSM Tree (immutable segments) underneath the hood. This balloons writes. It demands significantly more RAM to function. 

Here are the 4 main indexing structures it uses under the hood:

### 1. The Inverted Index (For Text)
This is the "Secret Sauce" of search engines. It works exactly like the **Index at the back of a textbook**.

*   **How it works:** Instead of storing "Doc 1 contains 'Apple'", it stores "The word 'Apple' appears in Doc 1, Doc 5, and Doc 9".
*   **Why it's fast:** To find "Apple", it doesn't scan every row. It just looks up "Apple" in the dictionary and instantly gets the list of IDs.
*   **Used for:** `text` fields (Full-text search).


Inverted Index can do exact match and fuzzy search. 
Fuzzy search would be slow if we searched through all the words in index and did "edit distance". Instead we use Levenshtein Automation. 

Elasticsearch doesn't scann. It builds a Finite State Automation (DFA) for your query term. Then this term dictionary in Lucene is stored as a prefix tree (FST - Finite State Transducer). The engine walks the Term Dictionary and Query Automation simultaneously. 

Fuzzy search on an inverted index is fast because it turns the problem into a graph traversal problem. It only visits the tiny slice of the term dictionary that could possibly match. 


### 2. BKD Trees (For Numbers, Dates, & Geo)
Standard Inverted Indexes are bad at ranges (e.g., "Price > 100"). For this, Elasticsearch uses **Block K-Dimensional (BKD) Trees**.

*   **How it works:** It organizes data into multi-dimensional blocks. Think of it like a "Quadtree" or "R-Tree" but for any data type.
*   **Why it's fast:** It can quickly discard huge chunks of data that don't fit the range.
*   **Used for:** `long`, `integer`, `date`, `geo_point` (Maps).

### 3. Doc Values (For Sorting & Aggregations)
The Inverted Index is great for finding *which* docs match, but terrible for questions like "What is the average price?".

*   **How it works:** This is **Columnar Storage** (like Parquet or Cassandra). It stores values by column, not by row.
*   **Why it's fast:** It loads all the "Price" values into memory in a compressed block to do math on them without loading the rest of the document.
*   **Used for:** `keyword`, `integer`, `date` (when sorting or grouping).

### 4. HNSW Graph (For AI Vectors)
This is the modern "AI" index.

*   **How it works:** It builds a **Hierarchical Navigable Small World** graph. It maps data as points in a 3D (or 1000D) space.
*   **Why it's fast:** It allows for "Approximate Nearest Neighbor" (kNN) search. It finds things that are *semantically* similar (e.g., "King" is close to "Queen"), even if they don't share any words.
*   **Used for:** `dense_vector` (Embeddings from OpenAI/HuggingFace).

***

### Summary Table

| Data Type | Index Structure | Best For |
| :--- | :--- | :--- |
| **Text** | **Inverted Index** | "Find documents containing 'Apple'" |
| **Numbers/Dates** | **BKD Tree** | "Find products between $50 and $100" |
| **Geo** | **BKD Tree** | "Find restaurants within 5km" |
| **Sorting/Aggs** | **Doc Values** | "Calculate average price per category" |
| **Vectors** | **HNSW Graph** | "Find images that look like this one" |