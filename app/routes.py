from flask import Blueprint, request, jsonify, current_app
from weaviate.classes.query import Filter
from weaviate.util import generate_uuid5
from utils import query_weaviate, match_category
from app.db import get_user_state, set_user_state
from app.handlers import process_user_input

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Welcome to the Flask App!"

@main.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 204  # ✅ early exit for CORS preflight

    try:
        print("🟡 /chat endpoint hit")

        data = request.get_json()
        print("🔢 Request JSON:", data)

        user_message = data.get('message')
        print("👵🏽 User message:", user_message)

        if not user_message:
            return jsonify({"error": "Message required"}), 400

        user_id = data.get("user_id", "anonymous")

        print(f"⬆️STATE BEFORE {user_id}: {get_user_state(user_id)}")

        logic_response = process_user_input(user_id, user_message)

        print("🤖 Final bot response:", logic_response)

        print(f"⬇️STATE AFTER {user_id}: {get_user_state(user_id)}")

        return jsonify({
            "text": logic_response.get("text", None),
            "messages": logic_response.get("messages", None),
            "products": logic_response.get("products", []),
            "options": logic_response.get("options", []),
            "pharmacies": logic_response.get("pharmacies", []),
            "followup_text": logic_response.get("followup_text", None)
        }), 200

    except Exception as e:
        print("🔥 ERROR in /chat:", str(e))
        return jsonify({"error": str(e)}), 500


@main.route('/items', methods=['GET'])
def get_items():
    name = request.args.get('name')
    category = request.args.get('category')
    price = request.args.get('price')

    try:
        client = current_app.weaviate_client
        collection = client.collections.get("Supplements")

        if name:
            filters = Filter.by_property("nombre").equal(name)
        elif category:
            filters = Filter.by_property("categoria").equal(category)
        elif price:
            filters = Filter.by_property("precio").greater_than(float(price))
        else:
            filters = None

        query = collection.query.fetch_objects(filters=filters)
        items = [obj.properties for obj in query.objects]
        return jsonify(items), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    try:
        required_fields = ["nombre", "precio", "inventario", "categoria", "descripcion", "ingredientes", "allergens", "usage", "recommended_for", "link", "image"]
        missing_fields = [item for item in required_fields if item not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        client = current_app.weaviate_client
        collection = client.collections.get("Supplements")

        object_uuid = generate_uuid5({"nombre": data["nombre"]})

        if collection.data.exists(object_uuid):
            return jsonify({"error": "Item already exists"}), 201

        collection.data.insert(data, uuid=object_uuid)
        return jsonify({"message": "Item added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/items/<string:name>', methods=['PUT'])
def update_item(name):
    data = request.get_json()
    try:
        client = current_app.weaviate_client
        collection = client.collections.get("Supplements")

        query = collection.query.fetch_objects(
            filters=Filter.by_property("nombre").equal(name)
        )
        items = query.objects

        if not items:
            return jsonify({"error": "Item not found"}), 404

        uuid = items[0].uuid
        # Ensure 'image' is present in update
        if "image" not in data:
            return jsonify({"error": "Missing field: image"}), 400
        collection.data.update(uuid=uuid, properties=data)
        return jsonify({"message": "Item updated successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/items/<string:name>', methods=['DELETE'])
def delete_item(name):
    try:
        client = current_app.weaviate_client
        collection = client.collections.get("Supplements")

        query = collection.query.fetch_objects(
            filters=Filter.by_property("nombre").equal(name)
        )
        items = query.objects

        if not items:
            return jsonify({"error": "Item not found"}), 404

        uuid = items[0].uuid
        collection.data.delete_by_id(uuid)
        return jsonify({"message": "Item deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
