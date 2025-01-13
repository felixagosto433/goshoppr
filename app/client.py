import os
import weaviate
from weaviate.classes.init import Auth

FLASK_ENV = os.getenv("FLASK_ENV", "development")

if FLASK_ENV == "production":
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_CLOUD_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_ADMIN_KEY")),
    )
    print("Connected to Weaviate Cloud.")
elif FLASK_ENV in ["development", "testing"]:
    client = weaviate.connect_to_local(
    host="127.0.0.1",  # Use a string to specify the host
    port=8080,
    grpc_port=50051,
)
    print("Connected to Local Weaviate.")
else:
    raise ValueError("Invalid FLASK_ENV. Please set it to 'production', 'development', or 'testing'.")
