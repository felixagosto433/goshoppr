import os
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
import os

# Load .env.staging manually
load_dotenv(".env.staging")

# Debugging: Check if environment variable is loaded
print("DEBUG: HEROKU_APP_NAME =", os.getenv("HEROKU_APP_NAME"))
print("DEBUG: WEAVIATE_ADMIN_KEY =", os.getenv("WEAVIATE_ADMIN_KEY"))
print("DEBUG: WEAVIATE_CLOUD_URL =", os.getenv("WEAVIATE_CLOUD_URL"))

# Open AI authentication
openai_key = os.getenv("OPENAI_APIKEY")
headers = {
    "X-OpenAI-Api-Key": openai_key,
}
print(f"Passed Open Ai {headers}")
heroku_app_name = os.getenv("HEROKU_APP_NAME")

def get_weaviate_client():
    """Ensures the client is persistent"""
    global client
    if client is None or not client.is_connected():
        print("🔄 Reconnecting to Weaviate...")
        cluster_url = os.getenv("WEAVIATE_CLOUD_URL")
        auth_key = os.getenv("WEAVIATE_ADMIN_KEY")

        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=cluster_url,
            auth_credentials=Auth.api_key(auth_key),
            headers=headers
        )
        print("✅ Connected to Weaviate Successfully!")
    return client

# if heroku_app_name == "vast-escarpment-05453":
#     client = weaviate.connect_to_weaviate_cloud(
#         cluster_url=os.getenv("WEAVIATE_CLOUD_URL"),
#         auth_credentials=Auth.api_key(os.getenv("WEAVIATE_ADMIN_KEY")),
#         headers=headers
#     )
#     print("✅ Connected to Weaviate Production Cloud.")
#     collection = client.collections.get("Supplements")

# elif heroku_app_name == "staging-goshoppr":
#     client = weaviate.connect_to_weaviate_cloud(
#         cluster_url=os.getenv("WEAVIATE_CLOUD_URL"),
#         auth_credentials=Auth.api_key(os.getenv("WEAVIATE_ADMIN_KEY")),
#         headers=headers
#     )
#     print("✅ Connected to Weaviate Staging Cloud.")
#     collection = client.collections.get("Supplements")
# else:
#     raise ValueError("Invalid Variables")

# # Reconnect function for tests
# def reconnect_weaviate():
#     global client
#     if not client.is_connected():
#         print("🔄 Reconnecting to Weaviate...")
#         client.connect()
#         print("✅ Weaviate Reconnected")