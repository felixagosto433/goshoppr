import gspread
import pandas as pd
import os
from dotenv import load_dotenv
import json
import time
import weaviate
from weaviate.classes.config import Property, DataType
from weaviate.classes.init import AdditionalConfig, Timeout, Auth
from weaviate.util import generate_uuid5

# Load environment variables
load_dotenv()

# Google Sheets authentication
SERVICE_KEY_PATH = os.getenv("SERVICE_KEY")
gc = gspread.service_account(filename=SERVICE_KEY_PATH)
sheet = gc.open('Go Shop Vector Database')  # Replace with your sheet name
worksheet = sheet.worksheet('Sheet1')  # Replace with your tab name
WEAVIATE_ADMIN_KEY = os.getenv("WEAVIATE_ADMIN_KEY")

# Connect to Weaviate
client = weaviate.connect_to_weaviate_cloud(
    cluster_url="https://pxplk2lvsey4xwtvdu1jeg.c0.us-east1.gcp.weaviate.cloud",
    auth_credentials=Auth.api_key(WEAVIATE_ADMIN_KEY),
    additional_config=AdditionalConfig(timeout=Timeout(init=10)),
)

# Test connection
if client.is_ready():
    print("Connected to Weaviate Cloud Service!")
else:
    print("Failed to connect.")

client.connect()
print("Connected to Weaviate!")

# Define the collection name
collection_name = "Supplements"

def fetch_google_sheets_data():
    # Fetch all records
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # Remove duplicates based on a unique column
    df = df.drop_duplicates(subset=["nombre"])

    # Transform data to JSON
    def transform_row(row):
        transformed = {
            "nombre": row["nombre"],
            "precio": float(row["precio"]),
            "inventario": float(row["inventario"]),
            "categoria": row["categoria"],
            "descripcion": row["descripcion"],
            "ingredientes": row["ingredientes"].split(', '),
            "allergens": row["allergens"].split(', '),
            "usage": row["usage"],
            "recommended_for": row["recommended_for"].split(', '),
            "link": row.get("link", None),
        }
        return transformed

    return [transform_row(row) for _, row in df.iterrows()]

def update_weaviate_schema(data):
    collection_exists = client.collections.exists(collection_name)
    if collection_exists:
        print(f"Collection '{collection_name}' found. Checking for schema updates...")
        collection = client.collections.get(collection_name)
        existing_properties = {prop.name for prop in collection.config.get().properties}

        # Dynamically add missing properties
        for field in data[0].keys():
            if field not in existing_properties:
                print(f"Adding new property: {field}")
                data_type = (
                    DataType.TEXT_ARRAY if isinstance(data[0][field], list)
                    else DataType.NUMBER if isinstance(data[0][field], (int, float))
                    else DataType.TEXT
                )
                collection.config.add_property(Property(name=field, data_type=data_type))

    else:
        print(f"Collection '{collection_name}' not found. Creating it...")
        properties = [
            Property(name=key, data_type=(DataType.TEXT_ARRAY if isinstance(value, list)
                                          else DataType.NUMBER if isinstance(value, (int, float))
                                          else DataType.TEXT))
            for key, value in data[0].items()
        ]
        client.collections.create(collection_name, properties=properties)
        print(f"Collection '{collection_name}' created successfully!")


def upload_data_to_weaviate(collection, data, max_retries=5, wait_time=30):
    for item in data:
        retries = 0
        while retries < max_retries:
            try:
                print(f"Uploading item: {item['nombre']}")
                # Generate a UUID based on a key property, e.g., "nombre"
                object_uuid = generate_uuid5({"nombre": item["nombre"]})

                if collection.data.exists(object_uuid):
                    print(f"Object '{item['nombre']}' already exists. Skipping...")
                else:
                    print(f"Uploading new object: {item['nombre']}")
                    collection.data.insert(item, uuid=object_uuid)
                    print(f"Object '{item['nombre']}' uploaded successfully!")
                break  # Exit retry loop if successful
            except Exception as e:
                error_message = str(e)
                if "model is currently loading" in error_message:
                    retries += 1
                    print(f"Model is still loading. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"An unexpected error occurred: {e}")
                    break  # Exit retry loop for non-retryable errors
        else:
            print(f"Failed to upload '{item['nombre']}' after {max_retries} retries. Skipping...")

try:
    # Fetch Google Sheets data
    json_data = fetch_google_sheets_data()
    print("Data fetched from Google Sheets!")

    # Update schema
    update_weaviate_schema(json_data)

    # Fetch the collection
    collection = client.collections.get(collection_name)

    # Upload data to Weaviate
    upload_data_to_weaviate(collection, json_data)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    client.close()
    print("Connection closed.")
