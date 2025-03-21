import streamlit as st
import requests
import pyodbc
from datetime import datetime
from funcy import connect_to_mariadb as cm
from mysql.connector import Error, IntegrityError

# API endpoint template
api_url_template = 'https://api.digikala.com/v2/product/{product_id}/'

# Function to fetch product IDs from the database
def fetch_product_ids():
    """
    Fetches all product IDs from the ProductDetails table in the MariaDB database.

    Returns:
        list: A list of product IDs.
    """
    connection = None
    try:
        # Establish a connection to the MariaDB database
        connection = cm()  # Assuming cm() is your connection function
        if not connection.is_connected():
            st.error("Failed to connect to the database.")
            return []

        cursor = connection.cursor()

        # Query to fetch product IDs
        query = "SELECT ProductID FROM ProductDetails"
        cursor.execute(query)

        # Fetch all rows and extract the first column (ProductID)
        product_ids = [row[0] for row in cursor.fetchall()]
        return product_ids

    except Error as e:
        st.error(f"Error fetching product IDs: {e}")
        return []

    finally:
        # Ensure the connection is closed properly
        if connection and connection.is_connected():
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
import mysql.connector
from mysql.connector import Error

def insert_into_product_prices(product_id, selling_price, discount, rrp_price, date):
        """
        Inserts a new record into the ProductPrices table.

        Args:
            product_id (int): The ID of the product.
            selling_price (float): The selling price of the product.
            discount (float): The discount percentage applied to the product.
            rrp_price (float): The recommended retail price (RRP) of the product.
            date (str): The date associated with the price data (format: 'YYYY-MM-DD').

        Returns:
            None
        """
    # Establish a connection to the MariaDB database
    # Assuming cm() is your connection function
        connection = cm()  
        if not connection:
            print("Failed to connect to the database.")
            return

        cursor = connection.cursor()

        # Define the SQL query with %s placeholders
        query = """
        INSERT INTO ProductPrices (
            product_id, 
            selling_price, 
            discount, 
            rrp_price, 
            date
        ) VALUES (%s, %s, %s, %s, %s)
        """

        # Prepare the values as a tuple
        values = (product_id, selling_price, discount, rrp_price, date)

        # Execute the query
        cursor.execute(query, values)

        # Commit the transaction
        connection.commit()
        connection.close()
        print("Record inserted successfully.")

    
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
    duplicate_count = 0
    # Create a container for the status box
    status_box = st.container()
    with status_box:
        st.subheader("Status Summary")
        col1, col2, col3 , col4 = st.columns(4)
        error_placeholder = col1.empty()
        duplicate_error = col2.empty()
        insert_placeholder = col3.empty()
        out_of_stock_placeholder = col4.empty()
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
                except IntegrityError as e:
                    # Handle duplicate entry error
                    if e.errno == 1062:
                        duplicate_count=+1
                        duplicate_error.error(f"Duplicate : {duplicate_count}")
                
                except KeyError as e:
                    error_count += 1
                    error_placeholder.error(f"Errors: {error_count}")
                    # st.error(f"KeyError: {e} in product ID {product_id}. Data might be missing in the API response.")
                except Exception as e:
                    error_count += 1
                    error_placeholder.error(f"Errors: {error_count}")
                    print(e)
                    # st.error(f"Unexpected error for product ID {product_id}: {e}")
            else:
                out_of_stock_count += 1
                out_of_stock_placeholder.warning(f"Out of Stock: {out_of_stock_count}")
                

# Run the Streamlit app
if __name__ == "__main__":
    main()