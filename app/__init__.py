from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .client import client

db = SQLAlchemy()

def create_app(config_class=None):
    app = Flask(__name__)

    # Apply configuration
    if config_class:
        app.config.from_object(config_class)

    db.init_app(app)
    # Skip database initialization if no URI is configured
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        db.init_app(app)
    else:
        print("No database configured. Skipping SQLAlchemy initialization.")
    
    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)
    return app
