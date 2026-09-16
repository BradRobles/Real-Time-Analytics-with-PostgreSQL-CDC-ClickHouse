# Real-Time E-commerce Analytics (PostgreSQL + ClickHouse)

This project implements a complete Change Data Capture (CDC) streaming pipeline in real-time for a simulated e-commerce store. It uses PostgreSQL as the transactional database (OLTP) and ClickHouse's `MaterializedPostgreSQL` engine for real-time analytical ingestion (OLAP), culminating in an interactive Streamlit dashboard.

## Prerequisites

To run this project on any computer, you only need to have the following installed:

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/)

You do not need to install Python, PostgreSQL, or ClickHouse locally, as everything is 100% containerized.

## Deployment Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/BradRobles/Real-Time-Analytics-with-PostgreSQL-CDC-ClickHouse.git
   cd Real-Time-Analytics-with-PostgreSQL-CDC-ClickHouse
   ```

2. **Spin up the services with Docker Compose**
   Run the following command in the root of the project (where the `docker-compose.yml` file is located):
   ```bash
   docker compose up -d --build
   ```
   *This will download the necessary images, initialize the databases, start the traffic generator, and launch the dashboard.*

3. **Verify the services**
   Make sure all 4 containers are running correctly:
   ```bash
   docker compose ps
   ```
   You should see the `postgres`, `clickhouse`, `generator`, and `dashboard` services in the "Up" state.

4. **Access the Dashboard**
   Open your web browser and visit:
   👉 **http://localhost:8501**

   You will see the revenue and order charts updating in real-time.

## Architecture

- **Generator (`generator/`):** Python script that continuously inserts and updates thousands of random orders in PostgreSQL.
- **PostgreSQL (`postgres/`):** Database configured with `wal_level = logical` and `REPLICA IDENTITY DEFAULT` on its tables to record every single change.
- **ClickHouse (`clickhouse/`):** Columnar analytical database. It connects to PostgreSQL's Logical Replication and clones every change into `ReplacingMergeTree` tables in milliseconds.
- **Dashboard (`dashboard/`):** Streamlit app that queries ClickHouse tables using `FINAL` filters to deduplicate records updated in real-time.

## Stopping the environment

To stop all containers and clean up resources, run:
```bash
docker compose down
```

*If you also want to clear the persistence (delete the data saved in the databases to start from scratch), add the `-v` flag:*
```bash
docker compose down -v
```
