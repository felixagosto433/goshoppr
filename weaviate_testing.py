import weaviate
import time
from dotenv import load_dotenv
import gspread
import os
from weaviate.classes.query import Filter
from weaviate.util import generate_uuid5
from flask import request
from weaviate.classes.init import AdditionalConfig, Timeout, Auth


# Connecting to local.
# client = weaviate.connect_to_local()

# while not client.is_ready():
#     print("Waiting for Weaviate to be ready...")
#     time.sleep(30)

# Cloud connection. 
load_dotenv()
WEAVIATE_ADMIN_KEY = os.getenv("WEAVIATE_ADMIN_KEY")

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

collections = client.collections.list_all()
print("______________CHECKING IF COLLECTIONS ARE PRESENT___________")
print(f"Existing collections: {collections.keys()}") 
collection = client.collections.get("Supplements")

# Google Sheets authentication
# SERVICE_KEY_PATH = os.getenv("SERVICE_KEY")
# gc = gspread.service_account(filename=SERVICE_KEY_PATH)
# sheet = gc.open('Go Shop Vector Database')  # Replace with your sheet name
# worksheet = sheet.worksheet('Sheet1')  # Replace with your tab name

# HUGGING_TOKEN = os.getenv("HUGGING_TOKEN")

# # Define the connection parameters properly
# client = weaviate.connect_to_local()
# # Initialize the Weaviate client
# client.connect()
# print("Connected!!!")

# SCHEMA CREATION AND DB POPULATION
# try:
#     # Check if the "Supplements" collection exists
#     collections = client.collections.list_all()
#     print(f"Existing collections: {collections.keys()}") 

#     if "Supplements" in collections:
#         print("Collection 'Supplements' already exists...")
#     else:
#         print("Creating 'Supplements' collection...")
#         client.collections.create(
#             "Supplements",
#             vectorizer_config=Configure.Vectorizer.text2vec_huggingface(),
#             properties=[
#         Property(name="nombre", data_type=DataType.TEXT, vectorizer_config={"skip": True}),
#         Property(name="categoria", data_type=DataType.TEXT),
#         Property(name="descripcion", data_type=DataType.TEXT),
#         Property(name="ingredientes", data_type=DataType.TEXT_ARRAY),
#         Property(name="usage", data_type=DataType.TEXT, vectorizer_config={"skip": True}),
#         Property(name="precio", data_type=DataType.NUMBER, vectorizer_config={"skip": True}),
#         Property(name="inventario", data_type=DataType.NUMBER, vectorizer_config={"skip": True}),
#         Property(name="link", data_type=DataType.TEXT, vectorizer_config={"skip": True}),
#     ],
#         )
#         print("Collection created successfully!!!")

#     # Load the collection
#     supplements_collection = client.collections.get("Supplements")

#     # Load JSON Data
#     with open("vitaminas.json", "r", encoding="utf-8") as file:
#         data = json.load(file)

#     # Insert each object into the collection
#     for obj in data:
#         supplements_collection.data.insert(obj)
#     print("Data imported successfully!")

# except Exception as e:
#     print(f"The following error occurred: {e}")

# finally:
#     client.close()
#     print("Connection closed. Done.")

# PRINT SCHEMA
print("_________________________________________")
print("SCHEMA")
print(collection)

# PRINT ALL OBJECTS
# print("_________________________________________")
# print("OBJECTS")
# for item in collection.iterator():
#     print("+++++++ID++++++++")
#     print(item.uuid)
#     print("+++++++PROPERTIES++++++++")
#     print(item.properties)

# PRINT RESPONSE
# response = collection.query.near_text(
#     query="Cartílago de Tiburón",
#     limit=5
# )

# print(f"Length of response: {len(response.objects)}")

# for obj in response.objects:
#     if "nombre" in response.objects:
#         print(obj.properties["nombre"])
#     else:
#         print("NO NAME FOUND")


# Viewing all arguments for collection. 
# config = collection.config.get()
# properties = {prop.name for prop in config.properties}
# print(properties)

# Hardcode Testing fetching by name property
# print("______________FETCHING BY PROPERTY___________")
# result = collection.query.fetch_objects(
#     filters=Filter.by_property("nombre").equal("Cartílago de Tiburón")
# )
# print("Query Result:", result.objects)

# Hardcode Testing fetching by category property
# print("______________FETCHING BY Category___________")
# result = collection.query.fetch_objects(
#     filters=Filter.by_property("categoria").equal("Acidos Grasos Omega")
# )
# print("Query Result:", result.objects)

# Hardcode testing for deleting item
# name = "Test Item"
# try:

#     # Find the item to delete
#     query = collection.query.fetch_objects(
#         filters=Filter.by_property("nombre").equal(name)
#     )
#     items = query.objects
#     if not items:
#         print("Item not found")
    
#     # Delete the item
#     uuid = items[0].uuid
#     print(f"This is the item id: {uuid}")
#     collection.data.delete_by_id(uuid)
#     print("Item deleted succesfully!")

# except Exception as e:
#     print(f"Error deleting item: {e}")

# Hardcode testing adding item, dupliate item logic, and missing fields logic.
test_item = {
            "nombre": "Test Item",
            "precio": 10.00,
            "inventario": 100,
            "categoria": "Test Category",
            "descripcion": "This is a test item.",
            "ingredientes": ["Test Ingredient"],
            "allergens": ["None"],
            "usage": "Test usage instructions.",
            "recommended_for": ["Test Use"],
            "link": "https://example.com/test-item"
        }

try:
    required_fields = ["nombre", "precio", "inventario", "categoria", "descripcion", "ingredientes", "allergens", "usage", "recommended_for", "link"]
    missing_fields = [item for item in required_fields if item not in test_item]

    if missing_fields:
        print(f"Some fields are missing: {missing_fields}")
    
    # Generate UUID based on "nombre"
    object_uuid = generate_uuid5({"nombre": test_item["nombre"]})
    collection = client.collections.get("Supplements")

    if collection.data.exists(object_uuid):
        print("Item already exists!")
    
    collection.data.insert(test_item, uuid=object_uuid)
    print('Item added Succesfully')

except Exception as e:
    print(f"Error found: {e}")

# Hardcode testing updating item
# name = "Test Item"
# data = {"precio": 12.99}
# try:

#     # Find the item using filtered name
#     query = collection.query.fetch_objects(
#         filters=Filter.by_property("nombre").equal(name)
#     )
#     items = query.objects

#     if not items:
#         print("Item not found")
    
#     # Update the item
#     uuid = items[0].uuid
#     collection.data.update(uuid=uuid, properties=data)
#     print("Item updated succesfully!")

# except Exception as e:
#     print(f"Error updating item: {e}")

# Hardcode testing for getting items with filters
# name = "Cartílago de Tiburón"
# category = "Salud Articular"
# price = 2.00

# try:
#     collection = client.collections.get("Supplements")

#     # Apply filters dynamically based on query parameters
#     if name:
#         filters = Filter.by_property("nombre").equal(name)
#     elif category:
#         filters = Filter.by_property("categoria").equal(category)
#     elif price:
#         filters = Filter.by_property("precio").greater_than(float(price))
#     else:
#         filters = None  # No filters applied

#     # Execute the query 
#     query = collection.query.fetch_objects(filters=filters)
#     items = [obj.properties for obj in query.objects]

#     print(f"Item got succesfully!: {items}")

# except Exception as e:
#     print(f"Error getting item: {e}")

# Deleting each item in the weaviate db by id
# try:
#     print(f"Clearing all data from the '{collection}' collection...")
#     collection = client.collections.get(collection)

#     for item in collection.iterator():
#         collection.data.delete_by_id(
#             item.uuid
#         )

#     print(f"All data from '{collection}' has been cleared!")
# except Exception as e:
#     print(f"An error occurred while clearing the collection: {e}")
# finally:
#     client.close()
#     print("Connection closed.")

client.close()

