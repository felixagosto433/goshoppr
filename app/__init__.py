from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .client import client

db = SQLAlchemy()  # Initialize SQLAlchemy instance

def create_app(config_class=None):
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)

    # Apply configuration if provided
    if config_class:
        app.config.from_object(config_class)

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
