import streamlit as st
import clickhouse_connect
import pandas as pd
import time
import os

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CH_USER = os.getenv("CLICKHOUSE_USER", "default")
CH_PASS = os.getenv("CLICKHOUSE_PASSWORD", "")

st.set_page_config(page_title="Real-Time Orders Dashboard", layout="wide")

@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASS, database='shop')

try:
    client = get_client()
except Exception as e:
    st.error(f"Waiting for ClickHouse... {e}")
    st.stop()

st.title("Real-Time E-commerce Analytics (PostgreSQL CDC + ClickHouse)")

placeholder = st.empty()

while True:
    try:
        # MaterializedPostgreSQL adds _sign (1 for valid, -1 for deleted) and uses ReplacingMergeTree
        # We must use FINAL and filter _sign = 1 to get the exact real-time state!
        
        query_orders = """
        SELECT status, count(*) as count 
        FROM postgres_db.orders FINAL
        WHERE _sign = 1
        GROUP BY status
        ORDER BY count DESC
        """
        
        df_orders = client.query_df(query_orders)
        
        query_revenue = """
        SELECT p.name, sum(p.price) as revenue
        FROM postgres_db.orders AS o FINAL
        JOIN postgres_db.products AS p FINAL ON o.product_id = p.id
        WHERE o._sign = 1 AND p._sign = 1 AND o.status != 'CANCELLED'
        GROUP BY p.name
        ORDER BY revenue DESC
        """
        df_revenue = client.query_df(query_revenue)

        with placeholder.container():
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Orders by Status")
                st.bar_chart(df_orders.set_index('status'))
                st.dataframe(df_orders)

            with col2:
                st.subheader("Revenue by Product (Excl. Cancelled)")
                st.bar_chart(df_revenue.set_index('name'))
                st.dataframe(df_revenue)
                
    except Exception as e:
        st.warning(f"Waiting for data to be synced into ClickHouse... ({e})")
    
    time.sleep(2)
