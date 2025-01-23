from flask import Blueprint, request, jsonify
from weaviate.classes.query import Filter
from weaviate.util import generate_uuid5
from .client import client
from utils import process_message

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Welcome to the Flask App!"

@main.route('/chat', methods = ['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify ({"error", "Message required"}), 400
        
        response = process_message(user_message, client)
        return jsonify ({"response", response}), 200
    except Exception as e:
        return jsonify ({"error", str(e)}), 500

def process_message(user_message, client):
    collection_object = client.collections.get("Supplements")
    try:
        response = collection_object.query.near_text(
            query = user_message,
            limit=5
        )

        # Parse response
        if response and response.objects:
            result_strings = [
                f"{obj.properties['nombre']} - {obj.properties['descripcion']} (${obj.properties['precio']})"
                for obj in response.objects
            ]
            print("\n".join(result_strings))

        print("No supplements found for your query. Please try a different category.")
    except Exception as e:
        print(f"An error occurred while processing your request: {str(e)}")


@main.route('/items', methods=['GET'])
def get_items():
    """
    Fetch items from Weaviate with optional query filters (name, category, price).
    """
    name = request.args.get('name')
    category = request.args.get('category')
    price = request.args.get('price')

    try:
        collection = client.collections.get("Supplements")

        # Apply filters dynamically based on query parameters
        if name:
            filters = Filter.by_property("nombre").equal(name)
        elif category:
            filters = Filter.by_property("categoria").equal(category)
        elif price:
            filters = Filter.by_property("precio").greater_than(float(price))
        else:
            filters = None  # No filters applied

        # Execute the query 
        query = collection.query.fetch_objects(filters=filters)
        items = [obj.properties for obj in query.objects]

        return jsonify(items), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/items', methods=['POST'])
def add_item():
    """
    Add a new item to Weaviate.
    """
    data = request.get_json()
    try:
        required_fields = ["nombre", "precio", "inventario", "categoria", "descripcion", "ingredientes", "allergens", "usage", "recommended_for", "link"]
        missing_fields = [item for item in required_fields if item not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400
        
        # Generate UUID based on "nombre"
        object_uuid = generate_uuid5({"nombre": data["nombre"]})
        collection = client.collections.get("Supplements")

        if collection.data.exists(object_uuid):
            return jsonify({"error": "Item already exists"}), 201
        
        collection.data.insert(data, uuid=object_uuid)
        return jsonify({"message": "Item added succesfully!"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/items/<string:name>', methods=['PUT'])
def update_item(name):
    """
    Update an existing item based on its 'nombre'.
    """
    data = request.get_json()
    try:
        collection = client.collections.get("Supplements")

        # Find the item using filtered name
        query = collection.query.fetch_objects(
            filters=Filter.by_property("nombre").equal(name)
        )
        items = query.objects

        if not items:
            return jsonify({"error": "Item not found"}), 404
        
        # Update the item
        uuid = items[0].uuid
        collection.data.update(uuid=uuid, properties=data)
        return jsonify({"message": "Item updated succesfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@main.route('/items/<string:name>', methods=['DELETE'])
def delete_item(name):
    """
    Delete an item from Weaviate based on its 'nombre'.
    """
    try:
        collection = client.collections.get("Supplements")

        # Find the item to delete
        query = collection.query.fetch_objects(
            filters=Filter.by_property("nombre").equal(name)
        )
        items = query.objects
        if not items:
            return jsonify({"error": "Item not found"}), 404
        
        # Delete the item
        uuid = items[0].uuid
        collection.data.delete_by_id(uuid)
        return jsonify({"message": "Item deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



