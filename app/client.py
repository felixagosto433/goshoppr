import os
import weaviate
from weaviate.classes.init import Auth

# Open AI authentication
openai_key = os.getenv("OPENAI_APIKEY")
headers = {
    "X-OpenAI-Api-Key": openai_key,
}

heroku_app_name = os.getenv("HEROKU_APP_NAME")

if heroku_app_name == "vast-escarpment-05453":
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_CLOUD_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_ADMIN_KEY")),
        headers=headers
    )
    print("✅ Connected to Weaviate Production Cloud.")
    collection = client.collections.get("Supplements")

elif heroku_app_name == "staging-goshoppr":
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_CLOUD_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_ADMIN_KEY")),
        headers=headers
    )
    print("✅ Connected to Weaviate Staging Cloud.")
    collection = client.collections.get("Supplements")
else:
    raise ValueError("Invalid FLASK_ENV. Please set it to 'production', 'development', or 'testing'.")

# Reconnect function for tests
def reconnect_weaviate():
    global client
    if not client.is_connected():
        print("🔄 Reconnecting to Weaviate...")
        client.connect()
        print("✅ Weaviate Reconnected")