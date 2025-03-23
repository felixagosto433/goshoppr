# app/client.py

import os
import weaviate
from weaviate.classes.init import Auth

# OpenAI authentication
openai_key = os.getenv("OPENAI_APIKEY")
headers = {"X-OpenAI-Api-Key": openai_key}

# Global cached client
_client_instance = None

def get_weaviate_client():
    """Returns a persistent Weaviate client connection"""
    global _client_instance

    heroku_app_name = os.getenv("HEROKU_APP_NAME")

    if _client_instance is None or not _client_instance.is_connected():
        print("🔄 Connecting to Weaviate...")
        cluster_url = os.getenv("WEAVIATE_CLOUD_URL")
        api_key = os.getenv("WEAVIATE_ADMIN_KEY")
        
        # Connect client
        _client_instance = weaviate.connect_to_weaviate_cloud(
            cluster_url=cluster_url,
            auth_credentials=Auth.api_key(api_key),
            headers=headers
        )

        print("✅ Connected to Weaviate!")

    return _client_instance

def close_weaviate_client():
    global _client_instance
    if _client_instance and _client_instance.is_connected():
        _client_instance.close()
        print("🔴 Closed Weaviate client")
        _client_instance = None
