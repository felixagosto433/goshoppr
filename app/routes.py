from flask import Blueprint, request, jsonify, current_app
from weaviate.classes.query import Filter
from weaviate.util import generate_uuid5
from utils import extract_concepts, query_weaviate

main = Blueprint('main', __name__)

# Temporary process user input logic:

chat_state = {} 

def process_user_input(user_id, user_message):
    # Initialize user_state if new
    if user_id not in chat_state:
        chat_state[user_id] = {
            "stage": "welcome",
            "context": {}
        }

    # First naming of variables
    state = chat_state[user_id]

    stage = state["stage"]
    ctx = state["context"]

    # === Stage 1: Welcome ===
    if stage =="welcome":
        state["stage"] = "main_menu"
        return {
            "text": "¡Hola! 👋 Soy tu asistente de salud de Xtravit. ¿En qué puedo ayudarte hoy?",
            "options": [
                "Ver productos recomendados",
                "Obtener asesoramiento personalizado para vitaminas y suplementos",
                "Resolver dudas sobre mis pedidos",
                "Conocer promociones especiales"
            ]
        }
    
    # === Stage 2: Main Menu ===
    if stage == "main_menu":
        if "recomendados" in user_message.lower():
            state["stage"] = "recommendation_category"
            return {
                "text": "Perfecto. ¿Qué estás buscando mejorar?",
                "options": [
                    "Energía y Vitalidad",
                    "Sueño y Relajación",
                    "Salud del Corazón",
                    "Sistema Inmunológico",
                    "Otro (especificar)"
                ]
            }
        
        elif "asesoramiento" in user_message.lower():
            state["stage"] = "personal_advice"
            return {
                "text": "Para darte las mejores recomendaciones, ¿cuál es tu objetivo principal de salud?" 
            }
        
        elif "pedidos" in user_message.lower():
            return {
                "text": "¿En qué puedo ayudarte con tu pedido?",
                "options": [
                    "Estado de mi pedido",
                    "Información de envío",
                    "Devoluciones",
                    "Métodos de pago"
                ]
            }
        
        elif "promociones" in user_message.lower():
            return {
                "text": "¡Excelente! ¿Te interesa recibir un cupón o ver productos en oferta?",
                "options": ["Sí, quiero un cupón", "Ver productos en oferta"]
            }
        
        else:
            return {
                "text": "Lo siento, no entendí eso. ¿Puedes escoger una opción del menú?",
                "options": [
                    "Ver productos recomendados",
                    "Obtener asesoramiento personalizado",
                    "Resolver dudas sobre mis pedidos",
                    "Conocer promociones especiales"
                ]
            }
        
    # === Stage 3: Category-Based Recommendation === 
    if stage == "recommendation_category":
        category_map = {
            "energía": ["energía", "fatiga", "vitalidad"],
            "sueño": ["sueño", "insomnia", "relajación"],
            "corazón": ["immune system", "immunity", "defense"],
            "otro": [] # fallback
        }   

        for key, val in category_map.items():
            if key in user_message.lower(): # If one of the categories in my category map is in the users message
                if val:
                    results = query_weaviate(val)
                    state["stage"] = "done"
                    return {
                        "text": f"Aquí tienes algunas recomendaciones para {key}:",
                        "products": results
                    }
                else:
                    state["stage"] = "custom_query"
                    return {"text": "Por favor, especifica lo que necesitas mejorar."}
                
        return {
            "text": "No entendí esa categoría. ¿Puedes escoger una de las siguientes?",
            "options": list(category_map.keys())
        }
    
    # === Stage 4: Custom Query Handling ===
    if stage == "custom_query":
        concepts = extract_concepts(user_message.lower())
        results = query_weaviate(concepts)
        return {
            "text": "Gracias por compartir. Aquí tienes algunas recomendaciones:",
            "products": results
        }
    
    # === Stage 5: Personalized Advice Flow ===
    if stage == "personal_advice":
        ctx["health_goal"] = user_message
        state["stage"] = "ask_medical"
        return {
            "text": "¿Tienes alguna condición médica o tomas medicamentos actualmente?"
        }
    
    elif stage == "ask_medical":
        ctx["medical"] = user_message
        state["stage"] = "ask_preference"
        return {
            "text": "¿Tienes alguna preferencia en el tipo de suplemento (vitaminas, minerales, hierbas)?"
        }
    
    elif stage == "ask_preference":
        ctx["preference"] = user_message
        # Form a query
        query_terms = [ctx["health_goal"], ctx["preference"]]
        results = query_weaviate(query_terms)
        state["stage"] = "done"
        return {
            "text": "Gracias por la información. Aquí tienes productos que podrían ayudarte:",
            "products": results
        }
    
    # === Default / fallback ===
    return {
        "text": "Lo siento, no entendí eso. ¿Puedes intentarlo de otra forma?"
    }

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

        print("👵🏽🆔 User state (Current USER_ID) before processing user input:", chat_state.get(user_id))

        logic_response = process_user_input(user_id, user_message)

        print("🤖 Final bot response:", logic_response)

        return jsonify({
            "text": logic_response["text"],
            "products": logic_response.get("products", []),
            "options": logic_response.get("options", [])
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
        required_fields = ["nombre", "precio", "inventario", "categoria", "descripcion", "ingredientes", "allergens", "usage", "recommended_for", "link"]
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
