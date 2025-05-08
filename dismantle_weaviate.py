import weaviate
from dotenv import load_dotenv
import os
from weaviate.classes.init import AdditionalConfig, Timeout, Auth

# Cloud connection. 
load_dotenv(".env.production")
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

# DELETE A COLLECTION

client.collections.delete("Supplements")  # THIS WILL DELETE THE SPECIFIED COLLECTION(S) AND THEIR OBJECTS
print("Collection succesfully deleted")

client.close()