1. Kibana (The Official Dashboard)
This is the standard tool for visualizing data (charts, graphs) and managing the cluster.

URL: http://localhost:5601
Best For:
- Dev Tools: Running queries (SQL, JSON) in a nice console.
- Discover: Browsing your raw data.
- Visualizations: Building pie charts, line graphs, etc.


2. Cerebro (The "Internals" Viewer)
This is a lightweight admin tool that is actually better than Kibana for seeing the "physical" layout of your cluster.

URL: http://localhost:9000
How to connect:
- Open the URL.
- In the "Node address" box, type: http://systems-elasticsearch:9200
- Click Connect.
Best For:
- Visualizing Shards: You can see exactly which square (shard) lives on which server.
- Cluster State: Seeing if nodes are Green/Yellow/Red.
- Index Management: Deleting indices with a click.
