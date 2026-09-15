# U1T01: Real-Time Analytics with PostgreSQL CDC & ClickHouse

## 1. Introduction
This document serves as the project report for the CDC implementation between PostgreSQL (OLTP) and ClickHouse (OLAP). The architecture has been containerized using Docker, allowing it to run anywhere using a single `docker compose up -d --build` command.

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

## 4. CDC Setup Considerations (ClickHouse Native CDC)
Initially, third-party tools like PeerDB were considered. However, modern versions of PeerDB require a massive microservices architecture (Temporal, Minio, 10+ containers). To maintain a lightweight, highly efficient Dockerized environment, we pivoted to **ClickHouse's Native `MaterializedPostgreSQL` engine**.

### Setup Steps:
1. **PostgreSQL Configuration**: The `wal_level` in `postgresql.conf` was set to `logical`. This allows Postgres to stream logical decoding events (inserts, updates, deletes) to ClickHouse via the replication slot. `max_replication_slots` and `max_wal_senders` were also configured.
2. **Replica Identity**: Run `ALTER TABLE ... REPLICA IDENTITY DEFAULT;` on the tables. This is a strict requirement for ClickHouse's CDC engine to track primary keys on updates/deletes without schema mismatch errors.
3. **ClickHouse Integration**: We enabled the experimental feature in ClickHouse (`SET allow_experimental_database_materialized_postgresql = 1`) and created the database natively linking it to PostgreSQL:
   ```sql
   CREATE DATABASE postgres_db 
   ENGINE = MaterializedPostgreSQL('postgres:5432', 'shop', 'admin', 'password');
   ```
4. **Target Handling in ClickHouse**: ClickHouse automatically pulls a full snapshot of the Postgres tables and then subscribes to the WAL replication slot. Under the hood, it creates tables using the `ReplacingMergeTree` engine. To handle updates and deletes in real-time, it adds a `_sign` column (1 for active, -1 for deleted) and a `_version` column. 
5. **Querying Data**: Since ClickHouse merges data asynchronously, analytical queries must utilize the `FINAL` keyword and filter by `_sign = 1` to resolve the exact real-time state of the records.

## 5. Benchmarking & Execution Plans
We provided `queries/benchmark.sql` containing heavy analytical queries.

*During the live test, the Python generator pumps thousands of operations.*
1. **Query 1**: Total Revenue by Product for Delivered Orders (Aggregation + Join).
2. **Query 2**: Daily order volume per user.
3. **Query 3**: Status Breakdown across time.

### Observations
- **PostgreSQL (`EXPLAIN ANALYZE`)**: Shows sequential scans on large tables unless heavily indexed. Updates and deletes create dead tuples (bloat), which significantly slows down complex aggregations while the data generator is rapidly modifying rows.
- **ClickHouse (`EXPLAIN`)**: Execution plans heavily utilize vectorized query execution. Despite using `FINAL` (which merges parts on read), ClickHouse massively outperforms Postgres on aggregations (SUM, COUNT) over millions of rows because its columnar storage engine only reads the specific columns involved in the query, skipping unrelated row data.

## 6. Real-Time Dashboard
A Streamlit dashboard connects directly to ClickHouse via HTTP (port 8123). As the Python script inserts or updates an order in PostgreSQL, the `MaterializedPostgreSQL` engine captures the WAL change instantly. The Streamlit dashboard (`localhost:8501`) polls these analytical queries every 2 seconds and accurately reflects the changing state, demonstrating a fully decoupled yet synced real-time analytics pipeline.
