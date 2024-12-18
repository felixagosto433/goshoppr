from flask import Flask, request, jsonify
from flask_cors import CORS
import weaviate_utils

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Welcome to the Supplement Chatbot API!"})

@app.route("/search", methods=["POST"])
def search():
    """
    Endpoint for searching supplements in Weaviate.
    Expects a JSON payload like {"query": "joint health"}
    """
    try:
        data = request.json
        concept = data.get("query", "")
        if not concept:
            return jsonify({"error": "Query cannot be empty"}), 400

        # Query Weaviate
        results = weaviate_utils.search_supplements(concept)
        if results:
            return jsonify({"results": results}), 200
        else:
            return jsonify({"error": "No results found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
