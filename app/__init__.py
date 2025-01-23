from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .client import client
import os

db = SQLAlchemy()  # Initialize SQLAlchemy instance

from config import config  # Import the configuration mapping dictionary

def create_app():
    app = Flask(__name__)

    # Dynamically load configuration based on FLASK_ENV
    config_name = os.getenv("FLASK_ENV", "development")  # Default to 'development' if not set
    if config_name in config:
        app.config.from_object(config[config_name])
    else:
        raise ValueError(f"Invalid configuration name: {config_name}")

    # Initialize the database if a URI is configured
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        print("Initializing database...")
        db.init_app(app)
    else:
        print("No database configured. Skipping SQLAlchemy initialization.")

    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app

