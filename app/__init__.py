from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .client import client
import os
from config import config  # Import the configuration mapping dictionary

def create_app(config_name=None):
    app = Flask(__name__)

    # Dynamically load configuration based on FLASK_ENV
    if config_name:
        if config_name in config:
            app.config.from_object(config[config_name])
        else:
            raise ValueError(f"Invalid configuration name: {config_name}")

    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app

