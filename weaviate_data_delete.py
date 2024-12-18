import weaviate
import time
from weaviate.classes.query import Filter

client = weaviate.connect_to_local()

while not client.is_ready():
    print("Waiting for Weaviate to be ready...")
    time.sleep(30)

collection = client.collections.get("Supplements")

def clear_weaviate_collection(collection_name):
    try:
        print(f"Clearing all data from the '{collection_name}' collection...")
        collection = client.collections.get(collection_name)

        for item in collection.iterator():
            collection.data.delete_by_id(
                item.uuid
            )

        print(f"All data from '{collection_name}' has been cleared!")
    except Exception as e:
        print(f"An error occurred while clearing the collection: {e}")
    finally:
        client.close()
        print("Connection closed.")

# Example usage
clear_weaviate_collection("Supplements")