import weaviate
from weaviate.classes.config import Property, DataType

# Connect to Weaviate
client = weaviate.connect_to_local()
client.connect()
print("Connected to Weaviate!")

# Define the collection name
collection_name = "Supplements"

# Add new link property to collection schema
new_properties = [
    {"name": "link", "data_type": DataType.TEXT}
]

try:
    # Fetch existing collection schema
    collection = client.collections.get(collection_name)
    config = collection.config.get()
    existing_properties = {prop.name for prop in config.properties}

    # Add new properties dynamically
    for prop in new_properties:
        if prop["name"] not in existing_properties:
            print(f"Adding new property: {prop['name']}")
            collection.config.add_property(
                Property(name=prop["name"], data_type=prop["data_type"]),
            )
        else: 
            print(f"Property '{prop['name']}' already exists. Skipping.")


except Exception as e:
    print(f"An error occurred while updating the schema: {e}")

finally:
    client.close()
    print("Connection closed.")
