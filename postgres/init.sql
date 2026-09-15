

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note: PeerDB requires REPLICA IDENTITY FULL or at least a primary key (which we have) for UPDATES/DELETES.
-- By default, tables with PK will have REPLICA IDENTITY DEFAULT, which logs old key. 
-- For full tracking, FULL is recommended for CDC.
ALTER TABLE users REPLICA IDENTITY DEFAULT;
ALTER TABLE products REPLICA IDENTITY DEFAULT;
ALTER TABLE orders REPLICA IDENTITY DEFAULT;

-- Pre-populate some products
INSERT INTO products (name, price) VALUES 
('Laptop', 999.99),
('Smartphone', 699.50),
('Headphones', 199.99),
('Monitor', 299.00),
('Keyboard', 99.99);
