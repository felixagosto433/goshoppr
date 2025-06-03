from flask import Flask
from .routes import main
from .client import get_weaviate_client 
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Simple CORS configuration
    CORS(app, 
         resources={r"/*": {
             "origins": "*",
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Accept"],
             "supports_credentials": True,
             "max_age": 3600
         }})

    app.register_blueprint(main)
    app.weaviate_client = get_weaviate_client()

    return app
