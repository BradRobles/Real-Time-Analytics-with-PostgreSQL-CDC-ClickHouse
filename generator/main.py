import os
import time
import random
import psycopg2
from faker import Faker
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME = os.getenv("POSTGRES_DB", "shop")

fake = Faker()
statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']

def get_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
            )
            conn.autocommit = True
            return conn
        except psycopg2.OperationalError as e:
            logger.warning(f"Database not ready, retrying in 5s... ({e})")
            time.sleep(5)

def main():
    conn = get_connection()
    cursor = conn.cursor()
    logger.info("Connected to PostgreSQL! Starting data generation...")

    user_ids = []
    product_ids = [1, 2, 3, 4, 5]  # Matches init.sql
    order_ids = []

    # Initial seed of users
    for _ in range(100):
        name = fake.name()
        cursor.execute("INSERT INTO users (name) VALUES (%s) RETURNING id;", (name,))
        user_ids.append(cursor.fetchone()[0])

    operations = 0
    while True:
        try:
            action = random.choices(['INSERT_USER', 'INSERT_ORDER', 'UPDATE_ORDER', 'DELETE_ORDER'], weights=[0.1, 0.6, 0.2, 0.1])[0]

            if action == 'INSERT_USER':
                name = fake.name()
                cursor.execute("INSERT INTO users (name) VALUES (%s) RETURNING id;", (name,))
                user_ids.append(cursor.fetchone()[0])
            
            elif action == 'INSERT_ORDER':
                if not user_ids: continue
                uid = random.choice(user_ids)
                pid = random.choice(product_ids)
                status = random.choice(statuses[:2]) # New orders are pending or processing
                cursor.execute("INSERT INTO orders (user_id, product_id, status) VALUES (%s, %s, %s) RETURNING id;", (uid, pid, status))
                order_ids.append(cursor.fetchone()[0])

            elif action == 'UPDATE_ORDER':
                if not order_ids: continue
                oid = random.choice(order_ids)
                new_status = random.choice(statuses[2:]) # Update to shipped, delivered, etc
                cursor.execute("UPDATE orders SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s;", (new_status, oid))

            elif action == 'DELETE_ORDER':
                if not order_ids: continue
                oid = random.choice(order_ids)
                cursor.execute("DELETE FROM orders WHERE id = %s;", (oid,))
                order_ids.remove(oid)

            operations += 1
            if operations % 1000 == 0:
                logger.info(f"Executed {operations} operations.")
            
            time.sleep(0.01) # fast generation (approx 100/s)

        except Exception as e:
            logger.error(f"Error during execution: {e}")
            conn.rollback()

if __name__ == '__main__':
    main()
