from flask import Flask
from .routes import main
from .client import get_weaviate_client 
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Debug-friendly CORS configuration
    CORS(app, 
         resources={r"/*": {
             "origins": "*",  # Allow all origins temporarily for debugging
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
             "supports_credentials": True,
             "expose_headers": ["Content-Length", "Content-Range"]
         }})

    app.register_blueprint(main)
    app.weaviate_client = get_weaviate_client()

    return app
