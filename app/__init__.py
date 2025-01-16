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

    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
