**TSVector** (Text Search Vector) is a special data type in Postgres designed for **Full Text Search**.

Think of it as a **pre-processed, sorted list of unique words** from your document.

### Why do we need it?
If you search for "running" in a normal text column:
*   `SELECT * FROM docs WHERE content LIKE '%running%'`
*   It is **slow** (scans every character).
*   It is **dumb** (won't find "run" or "runs").

### What TSVector does
When Postgres converts text to a TSVector (`to_tsvector('The quick brown fox jumps')`), it does three things:

1.  **Tokenization:** Splits the string into words.
2.  **Normalization (Stemming):** Converts words to their root form.
    *   "Jumps" → "jump"
    *   "Running" → "run"
3.  **Stop Word Removal:** Removes common noise words.
    *   "The", "a", "is", "of" are deleted.

### Example
**Original Text:**
`"The fat cats sat on the mat and ate the fat rats"`

**TSVector Representation:**
`'ate':9 'cat':3 'fat':2,11 'mat':7 'rat':12 'sat':4`

Notice what happened:
*   **Sorted:** Alphabetical order.
*   **Unique:** "fat" appears once, but lists positions `2` and `11`.
*   **Stemmed:** "cats" became "cat", "rats" became "rat".
*   **Cleaned:** "The", "on", "and" are gone.

### Why is it fast?
Because the list is **sorted**, Postgres can use a **GIN Index** (Generalized Inverted Index) to find documents instantly. It's like looking up a word in the index at the back of a textbook instead of reading the whole book.


----

Relevance score

Read [](file:///Users/davidkoh/devel/Systems/postgres/fulltext_search_demo.py#60-60), lines 60 to 90

The rank is a **Relevance Score** calculated by the `ts_rank` function.

It tells you **how well** the document matches your query. A higher number means a better match.

### How is it calculated?
The algorithm considers several factors:

1.  **Frequency:** How many times does the word appear? (More is better).
2.  **Density:** Are the words close together? (For multi-word queries).
3.  **Weights (A, B, C, D):** This is the most important part in our demo.

### The Weights in your Code
Look at how we defined the table in fulltext_search_demo.py:

```sql
setweight(to_tsvector(..., title), 'A') || 
setweight(to_tsvector(..., content), 'B')
```

We assigned:
*   **Weight A (1.0)** to the **Title**.
*   **Weight B (0.4)** to the **Content**.

### Why "Database Indexing" got 0.6687
1.  The word "Database" appeared in the **Title** ("Database Indexing").
2.  Because it was in the Title (Weight A), it got a huge score boost.

### Why "PostgreSQL Tutorial" got 0.2432
1.  The word "database" appeared in the **Content** ("...relational database system").
2.  It did NOT appear in the Title.
3.  Because it was only in the Content (Weight B), it got a lower score.

So the rank effectively says: *"I found the word in the Title, so this document is probably more relevant than the one where I just found it buried in the text."*