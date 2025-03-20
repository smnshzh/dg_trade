import streamlit as st
import requests
import pyodbc
from datetime import datetime

# Database connection details
def connect_to_sql_server():
    server = '.'  # SQL Server name
    database = 'marketing'  # Database name
    username = 'sa'  # Username
    password = '123456'  # Password
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    try:
        return pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# API endpoint template
api_url_template = 'https://api.digikala.com/v2/product/{product_id}/'

# Function to fetch product IDs from the database
def fetch_product_ids():
    connection = None
    try:
        connection = connect_to_sql_server()
        if not connection:
            return []

        cursor = connection.cursor()

        # Query to fetch product IDs
        query = "SELECT [ProductID] FROM [marketing].[dbo].[ProductDetails]"
        cursor.execute(query)
        product_ids = [row.ProductID for row in cursor.fetchall()]
        return product_ids
    except pyodbc.Error as e:
        st.error(f"Error fetching product IDs: {e}")
        return []
    finally:
        if connection:
            connection.close()

# Function to fetch product data from the API
def fetch_product_data(product_id):
    url = api_url_template.format(product_id=product_id)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"Failed to fetch data for product ID {product_id}. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        st.error(f"Request error for product ID {product_id}: {e}")
        return None

# Function to insert data into the ProductPrices table
def insert_into_product_prices(product_id, selling_price, discount, rrp_price, date):
    connection = connect_to_sql_server()
    if not connection:
        return

    cursor = connection.cursor()

    # Insert query
    query = """
    INSERT INTO ProductPrices (product_id, selling_price, discount, rrp_price, date)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, product_id, selling_price, discount, rrp_price, date)
    connection.commit()
    connection.close()

# Streamlit app
def main():
    st.title("Digikala Product Data Fetcher")

    # Fetch product IDs from the database
    product_ids = fetch_product_ids()
    if not product_ids:
        st.warning("No product IDs found in the database.")
        return

    # Display product IDs
    st.write(f"Fetched {len(product_ids)} product IDs from the database.")

    # Initialize counters
    error_count = 0
    insert_count = 0
    out_of_stock_count = 0

    # Create a container for the status box
    status_box = st.container()
    with status_box:
        st.subheader("Status Summary")
        col1, col2, col3 = st.columns(3)
        error_placeholder = col1.empty()
        insert_placeholder = col2.empty()
        out_of_stock_placeholder = col3.empty()
        processing = st.empty()
    # Button to start fetching and inserting data
    if st.button("Fetch and Insert Data"):
        for product_id in product_ids:
            processing.text(f"{product_id} is under processing ...")

            product_data = fetch_product_data(product_id)

            if product_data and product_data['data']['product']["status"] != "out_of_stock":
                try:
                    # Extract required fields from the JSON response
                    selling_price = product_data['data']['product']['default_variant']['price']['selling_price']
                    discount = product_data['data']['product']['default_variant']['price']['discount_percent']
                    rrp_price = product_data['data']['product']['default_variant']['price']['rrp_price']
                    date = datetime.now().date()  # Current date

                    # Insert data into the database
                    insert_into_product_prices(int(product_id), selling_price, discount, rrp_price, date)
                    insert_count += 1
                    insert_placeholder.success(f"Inserted: {insert_count}")
                except KeyError as e:
                    error_count += 1
                    error_placeholder.error(f"Errors: {error_count}")
                    # st.error(f"KeyError: {e} in product ID {product_id}. Data might be missing in the API response.")
                except Exception as e:
                    error_count += 1
                    error_placeholder.error(f"Errors: {error_count}")
                    # st.error(f"Unexpected error for product ID {product_id}: {e}")
            else:
                out_of_stock_count += 1
                out_of_stock_placeholder.warning(f"Out of Stock: {out_of_stock_count}")
                

# Run the Streamlit app
if __name__ == "__main__":
    main()