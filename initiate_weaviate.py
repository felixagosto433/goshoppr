import weaviate
from dotenv import load_dotenv
import os
from weaviate.classes.init import AdditionalConfig, Timeout, Auth
from weaviate.classes.config import Property, DataType, Configure
import json

# Cloud connection. 
load_dotenv(".env.staging")
WEAVIATE_ADMIN_KEY = os.getenv("WEAVIATE_ADMIN_KEY")

# Open AI authentication
openai_key = os.getenv("OPENAI_APIKEY")
api_key = os.getenv("WEAVIATE_ADMIN_KEY")
headers = {"X-OpenAI-Api-Key": openai_key}

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_CLOUD_URL"),
    auth_credentials=Auth.api_key(api_key),
    additional_config=AdditionalConfig(timeout=Timeout(init=10)),
    headers=headers
)

# Test connection
if client.is_ready():
    print("Connected to Weaviate Cloud Service!")
else:
    print("Failed to connect.")

try:
    # Check if the "Supplements" collection exists
    collections = client.collections.list_all()
    print(f"Existing collections: {collections.keys()}") 

    if "Supplements" in collections:
        print("Collection 'Supplements' already exists...")
    else:
        print("Creating 'Supplements' collection...")
        client.collections.create(
            "Supplements",
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            properties=[
        Property(name="nombre", data_type=DataType.TEXT, vectorizer_config={"skip": True}),
        Property(name="categoria", data_type=DataType.TEXT),
        Property(name="descripcion", data_type=DataType.TEXT),
        Property(name="ingredientes", data_type=DataType.TEXT_ARRAY),
        Property(name="usage", data_type=DataType.TEXT, vectorizer_config={"skip": True}),
        Property(name="precio", data_type=DataType.NUMBER, vectorizer_config={"skip": True}),
        Property(name="inventario", data_type=DataType.NUMBER, vectorizer_config={"skip": True}),
        Property(name="link", data_type=DataType.TEXT, vectorizer_config={"skip": True}),
    ],
        )
        print("Collection created successfully!!!")

    # Load the collection
    supplements_collection = client.collections.get("Supplements")

    # Load JSON Data
    with open("vitaminas.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Insert each object into the collection
    for obj in data:
        supplements_collection.data.insert(obj)
    print("Data imported successfully!")

    # PRINT SCHEMA
    print("_________________________________________")
    print("SCHEMA")
    print(supplements_collection)

    # PRINT ALL OBJECTS
    print("_________________________________________")
    print("OBJECTS")
    for item in supplements_collection.iterator():
        print("+++++++ID++++++++")
        print(item.uuid)
        print("+++++++PROPERTIES++++++++")
        print(item.properties)

except Exception as e:
    print(f"The following error occurred: {e}")

finally:
    client.close()
    print("Connection closed. Done.")

supplements_collection = client.collections.get("Supplements")


