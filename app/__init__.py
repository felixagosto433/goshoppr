from flask import Flask
from .routes import main
from .client import get_weaviate_client 
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # 🔧 Apply full CORS config
    #CORS(app, resources={r"/*": {"origins": "https://bananos.mybigcommerce.com"}}, 
    #     methods=["GET", "POST", "OPTIONS"],
    #     allow_headers=["Content-Type"])
    CORS(app)

    app.register_blueprint(main)
    app.weaviate_client = get_weaviate_client()

    return app


# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from .client import get_weaviate_client
# import os
# from config import config  # Import the configuration mapping dictionary

# def create_app(config_name=None):
#     # Because config_name=None, the FLAS_ENV variable is used. 
#     app = Flask(__name__)

#     # Use the environment variable of the heroku app name
#     env = os.getenv("HEROKU_APP_NAME")

#     if env == "staging-goshoppr":
#         config_name = "staging"
#     elif env == "vast-escarpment-05453":
#         config_name = "production"
#     else:
#         config_name = os.getenv("FLASK_ENV", "staging")  # Default to development
#     if config_name:
#         if config_name in config:
#             app.config.from_object(config[config_name])
#         else:
#             raise ValueError(f"Invalid configuration name: {config_name}")

#     # Import and register blueprints
#     from .routes import main
#     app.register_blueprint(main)

#     return app

