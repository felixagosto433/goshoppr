from flask import Flask
from .routes import main
from .client import get_weaviate_client 
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # ✅ Only allow BigCommerce origin
    CORS(app, resources={r"/*": {"origins": "https://goshop.mybigcommerce.com"}},
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type"])

    app.register_blueprint(main)
    app.weaviate_client = get_weaviate_client()

    return app
