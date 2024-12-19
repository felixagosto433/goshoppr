import weaviate
import os
from dotenv import load_dotenv
from weaviate.classes.init import AdditionalConfig, Timeout, Auth

load_dotenv()

WEAVIATE_ADMIN_KEY = os.getenv("WEAVIATE_ADMIN_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url="https://e9crkmaxsxea5xwram0vkw.c0.europe-west3.gcp.weaviate.cloud",
    auth_credentials=Auth.api_key(WEAVIATE_ADMIN_KEY),
    additional_config=AdditionalConfig(timeout=Timeout(init=10)),
)

# Test connection
if client.is_ready():
    print("Connected to Weaviate Cloud Service!")
else:
    print("Failed to connect.")

client.close()
