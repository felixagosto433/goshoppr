import json
import weaviate
from weaviate.classes.config import Property, DataType, Configure
from dotenv import load_dotenv
import os

load_dotenv()

HUGGING_TOKEN = os.getenv("HUGGING_TOKEN")

# Define the connection parameters properly
client = weaviate.connect_to_local()
# Initialize the Weaviate client
client.connect()
print("Connected!!!")

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
            vectorizer_config=Configure.Vectorizer.text2vec_huggingface(),
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

except Exception as e:
    print(f"The following error occurred: {e}")

finally:
    client.close()
    print("Connection closed. Done.")

