from flask import Flask
from .routes import main
from .client import get_weaviate_client 
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Simple CORS configuration
    CORS(app, 
         origins=["https://goshop.mybigcommerce.com", "http://localhost:3000", "http://localhost:5000"],
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
         supports_credentials=True)

    app.register_blueprint(main)
    app.weaviate_client = get_weaviate_client()

    return app
