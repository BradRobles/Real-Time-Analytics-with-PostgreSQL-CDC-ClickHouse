SET allow_experimental_database_materialized_postgresql = 1;
CREATE DATABASE IF NOT EXISTS shop;

-- Set up the MaterializedPostgreSQL database engine
-- This natively connects to Postgres's logical replication slot and pulls CDC changes automatically
-- No third-party tools required!
CREATE DATABASE IF NOT EXISTS postgres_db
ENGINE = MaterializedPostgreSQL(
    'postgres:5432', 
    'shop', 
    'admin', 
    'password'
);

-- MaterializedPostgreSQL automatically creates ReplacingMergeTree tables for all synced tables!
-- Wait for syncing to start (handled automatically by the ClickHouse engine in the background)
