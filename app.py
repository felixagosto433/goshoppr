from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://bananos.mybigcommerce.com"])

from app.routes import main
app.register_blueprint(main)