-- Query 1: Total Revenue by Product for Delivered Orders
-- PostgreSQL
EXPLAIN ANALYZE 
SELECT p.name, SUM(p.price) 
FROM orders o 
JOIN products p ON o.product_id = p.id 
WHERE o.status = 'DELIVERED' 
GROUP BY p.name;

-- ClickHouse
EXPLAIN 
SELECT p.name, sum(p.price) 
FROM postgres_db.orders p_o 
JOIN postgres_db.products p ON p_o.product_id = p.id 
WHERE p_o.status = 'DELIVERED'
GROUP BY p.name;

-- Query 2: Daily order volume per user (top 10 active users)
-- PostgreSQL
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as total_orders
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.name
ORDER BY total_orders DESC
LIMIT 10;

-- ClickHouse
EXPLAIN
SELECT u.name, count(o.id) as total_orders
FROM postgres_db.users AS u FINAL
JOIN postgres_db.orders AS o FINAL ON u.id = o.user_id
WHERE o._sign = 1 AND u._sign = 1
GROUP BY u.name
ORDER BY total_orders DESC
LIMIT 10;

-- Query 3: Conversion Rate or Status Breakdown across time
-- PostgreSQL
EXPLAIN ANALYZE
SELECT DATE(updated_at) as day, status, COUNT(*)
FROM orders
GROUP BY day, status
ORDER BY day DESC;

-- ClickHouse
EXPLAIN
SELECT toDate(updated_at) as day, status, count(*)
FROM postgres_db.orders FINAL
WHERE _sign = 1
GROUP BY day, status
ORDER BY day DESC;
