import os
import weaviate
from weaviate.classes.init import Auth
from flask import Flask
import logging
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from config import config
import os

load_dotenv()

db = SQLAlchemy()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv("WEAVIATE_CLOUD_URL") and os.getenv("WEAVIATE_ADMIN_KEY"):
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_CLOUD_URL"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_ADMIN_KEY")),
    )
    logger.info("Connected to Weaviate Cloud.")

elif os.getenv("WEAVIATE_LOCAL_URL"):
    client = weaviate.connect_to_local()
    logger.info("Connected to Local Weaviate.")
    
else:
    logger.error("Weaviate configuration is missing.")
    raise ValueError("Weaviate configuration is missing. Please set the appropriate environment variables.")

def create_app(config_class=None):
    app = Flask(__name__)

    # Apply the configuration if provided
    env = os.getenv('FLASK_ENV', 'development')  # Default to 'development'
    app.config.from_object(config.get(env, config['development']))

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Default config

    db.init_app(app)

    # Import blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
