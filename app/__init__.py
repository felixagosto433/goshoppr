from flask import Flask
from .routes import main
from .client import get_weaviate_client 
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Enhanced CORS configuration for BigCommerce domain
    CORS(app, resources={r"/*": {
        "origins": "https://goshop.mybigcommerce.com",
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin"
        ],
        "expose_headers": ["Content-Length", "Content-Range"],
        "supports_credentials": True,
        "max_age": 3600  # Cache preflight requests for 1 hour
    }})

    app.register_blueprint(main)
    app.weaviate_client = get_weaviate_client()

    return app
