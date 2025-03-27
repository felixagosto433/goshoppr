from app import create_app
from flask_cors import CORS

app = create_app()
print("✅ App created with blueprint + weaviate")
CORS(app, origins=["https://bananos.mybigcommerce.com"])

