
The cities table is actually storing the **explicit Lat/Lon**, but it stores them in a binary format called **WKB (Well-Known Binary)**, which looks like a long hexadecimal string when you view it directly.

If you run `SELECT * FROM cities;`, you probably see something like:
`0101000020E6100000...`

This is **NOT a Geohash**.

### The Difference
1.  **WKB (What Postgres uses):**
    *   It is the raw binary representation of two 64-bit floating point numbers (Latitude and Longitude).
    *   It is exact. It preserves the full precision of the coordinates you inserted.
    *   It is optimized for the computer to do math on (distance, intersection).

2.  **Geohash:**
    *   It is a string compression method (e.g., `9q8yy`).
    *   It is **approximate**. It represents a rectangular "bucket" or area, not an exact point.
    *   Postgres *can* generate Geohashes (`ST_GeoHash(location)`), but it doesn't store points that way by default because you would lose precision.

### How to see the Lat/Lon
To see the human-readable coordinates, you have to ask PostGIS to convert the binary back to text:

```sql
SELECT name, ST_AsText(location) FROM cities;
```
**Output:** `POINT(-122.4194 37.7749)`

Or to get the raw numbers:
```sql
SELECT name, ST_X(location) as lon, ST_Y(location) as lat FROM cities;
