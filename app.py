from app import create_app
from flask_cors import CORS

# Initialize Flask app
app = create_app()  # Ensure this works with Gunicorn
CORS(app, origins=["https://bananos.mybigcommerce.com"])  # Enable cross-origin requests
