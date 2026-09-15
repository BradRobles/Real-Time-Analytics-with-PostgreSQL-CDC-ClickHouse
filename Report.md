# U1T01: Real-Time Analytics with PostgreSQL CDC & ClickHouse

## 1. Introduction
This document serves as the project report for the CDC implementation between PostgreSQL (OLTP) and ClickHouse (OLAP). The architecture has been containerized using Docker, allowing it to run anywhere using a single `docker compose up` command.

## 2. ER Model (Relational Modeling)
The database models an e-commerce fast-paced domain in 3NF (Third Normal Form).

**Entities & Relationships:**
- `users` (id PK, name, created_at)
- `products` (id PK, name, price)
- `orders` (id PK, user_id FK, product_id FK, status, updated_at)

A user can have multiple orders. A product can be referenced in multiple orders. This enables analytical aggregations on sales data.

## 3. Data Generation
A Python script utilizing `psycopg2` and `Faker` continuously pumps data into PostgreSQL.
The script performs the following randomly distributed operations:
- **10% INSERT_USER**: Adds new users to the platform.
- **60% INSERT_ORDER**: Creates new 'PENDING'/'PROCESSING' orders.
- **20% UPDATE_ORDER**: Modifies the status of existing orders to 'SHIPPED' or 'DELIVERED'.
- **10% DELETE_ORDER**: Deletes orders to simulate cancellations.

## 4. CDC Setup Considerations (PeerDB)
We utilized **PeerDB** to implement Change Data Capture (CDC). 

### Setup Steps:
1. **PostgreSQL Configuration**: The `wal_level` in `postgresql.conf` was set to `logical`, which allows Postgres to stream logical decoding events (inserts, updates, deletes) rather than just crash-recovery data.
2. **Replica Identity**: Run `ALTER TABLE ... REPLICA IDENTITY FULL;` on the tables. This ensures that UPDATE and DELETE statements include the previous values, which CDC tools like PeerDB need to correctly identify which record changed on the ClickHouse side.
3. **PeerDB Integration**: Spun up `peerdb-server` and `peerdb-ui`. 
4. **Target Handling in ClickHouse**: Since ClickHouse is an OLAP database, it relies on an append-only structure. Standard `UPDATE` and `DELETE` commands are expensive. To handle CDC mutations, we use the `ReplacingMergeTree` table engine with a `_is_deleted` column and a `_version` column. PeerDB handles this automatically via Mirrors. Analytical queries utilize the `FINAL` keyword to resolve the most recent record state on the fly.

### Running PeerDB Mirror:
Once the containers are up, the mirror can be established via the PeerDB UI (localhost:3000) or via a SQL command connected to PeerDB (localhost:9922).
```sql
-- Connect to PeerDB
-- psql -h localhost -p 9922 -U peerdb -d peerdb

CREATE PEER postgres_peer FROM postgresql WITH (
  host = 'postgres', port = 5432, user = 'admin', password = 'password', database = 'shop'
);

CREATE PEER clickhouse_peer FROM clickhouse WITH (
  host = 'clickhouse', port = 9000, user = 'default', password = '', database = 'shop'
);

CREATE MIRROR shop_mirror FROM postgres_peer TO clickhouse_peer WITH (
  table_mapping = '{
    "users": "users",
    "products": "products",
    "orders": "orders"
  }'
);
```

## 5. Benchmarking & Execution Plans
We provided `queries/benchmark.sql` containing heavy analytical queries.

*During the live test, the Python generator pumps thousands of operations.*
1. **Query 1**: Total Revenue by Product for Delivered Orders (Aggregation + Join).
2. **Query 2**: Daily order volume per user.
3. **Query 3**: Status Breakdown across time.

### Observations (To be filled when executed locally)
- **PostgreSQL (`EXPLAIN ANALYZE`)**: Shows sequential scans on large tables unless heavily indexed. Updates and deletes create dead tuples (bloat), which affects query times while the data generator is active.
- **ClickHouse (`EXPLAIN`)**: Execution plans heavily utilize vectorized query execution and primary key sparse indexing. Despite using `FINAL` (which has a performance penalty as it merges parts on read), ClickHouse significantly outperforms Postgres on aggregations (SUM, COUNT) and grouping over millions of rows because it is a columnar database reading only the required columns.

## 6. Real-Time Dashboard
A Streamlit dashboard connects directly to ClickHouse. As the Python script inserts or updates an order in PostgreSQL, PeerDB captures the WAL change and pushes it to ClickHouse. The Streamlit dashboard automatically re-runs the analytical queries and reflects the changed state, demonstrating a fully decoupled yet synced real-time analytics pipeline.
