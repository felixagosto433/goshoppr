from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class=None):
    app = Flask(__name__)

    # Apply the configuration if provided
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Default config

    db.init_app(app)

    # Import blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
