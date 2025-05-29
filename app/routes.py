from flask import Blueprint, request, jsonify, current_app
from weaviate.classes.query import Filter
from weaviate.util import generate_uuid5
from utils import extract_concepts, query_weaviate, match_category
from app.db import get_user_state, set_user_state

main = Blueprint('main', __name__)

# Temporary process user input logic:

def process_user_input(user_id, user_message):
    # Get user state from DB
    state = get_user_state(user_id)

    if not state:
        # First-time user
        state = {
            "stage": "welcome",
            "context": {}
        }
        set_user_state(user_id, state)

    stage = state["stage"]
    ctx = state["context"]

    # ✅ Force welcome message on empty message
    if user_message.strip() == "":
        state["stage"] = "main_menu"
        set_user_state(user_id, state)
        return {
            "text": "Soy tu asistente de salud de Xtravit 👋. ¿Qué deseas hacer hoy?",
            "options": [
                "Catálogo de Productos 💊",
                "Ayuda Personalizada de Suplementos 💡",
                "Dudas sobre mis pedidos 📦",
                "Promociones especiales 💸"
            ]
        }

    # === Stage 1: Welcome ===
    if stage == "welcome":
        state["stage"] = "main_menu"
        set_user_state(user_id, state)
        return {
            "text": "¡Hola! 👋 Soy tu asistente de salud de Xtravit. ¿En qué puedo ayudarte hoy?",
            "options": [
                "Catálogo de Productos 💊",
                "Ayuda Personalizada de Suplementos 💡",
                "Dudas sobre mis pedidos 📦",
                "Promociones especiales 💸"
            ]
        }

    # === Stage 2: Main Menu ===
    if stage == "main_menu":
        if "Catálogo" in user_message.lower() or "recomendados" in user_message.lower():
            state["stage"] = "recommendation_category"
            set_user_state(user_id, state)
            return {
                "text": "Perfecto. ¿Qué estás buscando mejorar?",
                "options": [
                    "Energía y Vitalidad",
                    "Sueño y Relajación",
                    "Salud del Corazón",
                    "Apoyo Immune",
                    "Salud Digestiva",
                    "Otro (especificar)"
                ]
            }
        elif "asesoramiento" in user_message.lower():
            state["stage"] = "personal_advice"
            set_user_state(user_id, state)
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
            state["stage"] = "custom_query"
            set_user_state(user_id, state)
            return {
                "text": "No entendí esa opción. ¿Podrías describir lo que te interesa en tus propias palabras?"
            }

    # === Stage 3: Category-Based Recommendation === 
    if stage == "recommendation_category":
        category_map = {
            "articular": ["articulaciones", "movilidad", "huesos", "músculos"],
            "hombres": ["testosterona", "masculinidad", "prostata", "impulso sexual", "esperma", "urinario"], 
            "higado": ["hígado", "hepáticos", "renal"], 
            "sueño": ["sueño", "melatonina", "relajación", "dormir", "descanso"],
            "energía": ["energía", "fatiga", "vitalidad", "multivitaminas"],
            "digestión": ["digestión", "probióticos", "salud intestinal", "hinchazón", "estómago", "gastrointestinal", "malestar"],
            "corazón": ["corazón", "presión arterial", "colesterol"],
            "inmunidad": ["inmunidad", "defensas", "sistema inmune"],
            "omega": ["cardiovascular", "cerebral", "ácidos grasos", "EPA", "DHA"],
            "otro": []
        }

        matched_keywords, matched_category = match_category(user_message, category_map)

        if matched_keywords:
            results = query_weaviate(matched_keywords)
            state['stage'] = "done"
            set_user_state(user_id, state)

        if matched_keywords:
            results = query_weaviate(matched_keywords)
            state["stage"] = "done"
            set_user_state(user_id, state)
            return {
                "text": f"Aquí tienes algunas recomendaciones para {matched_category}:",
                "products": results
            }
        else:
            state["stage"] = "custom_query"
            set_user_state(user_id, state)
            return {
                "text": "Por favor, especifica lo que necesitas mejorar."
            }

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
        state["context"] = ctx
        state["stage"] = "ask_medical"
        set_user_state(user_id, state)
        return {
            "text": "¿Tienes alguna condición médica o tomas medicamentos actualmente?"
        }

    elif stage == "ask_medical":
        ctx["medical"] = user_message
        state["context"] = ctx
        state["stage"] = "ask_preference"
        set_user_state(user_id, state)
        return {
            "text": "¿Tienes alguna preferencia en el tipo de suplemento (vitaminas, minerales, hierbas)?"
        }

    elif stage == "ask_preference":
        ctx["preference"] = user_message
        state["context"] = ctx
        query_terms = [ctx["health_goal"], ctx["preference"]]
        results = query_weaviate(query_terms)
        state["stage"] = "done"
        set_user_state(user_id, state)
        return {
            "text": "Gracias por la información. Aquí tienes productos que podrían ayudarte:",
            "products": results
        }

    # === Stage 6: Repeat flow ===
    if stage == "done":
        state["stage"] = "main_menu"
        set_user_state(user_id, state)
        return {
            "text": "¿Te puedo ayudar con algo más?",
            "options": [
                "Ver productos recomendados",
                "Obtener asesoramiento personalizado para vitaminas y suplementos",
                "Resolver dudas sobre mis pedidos",
                "Conocer promociones especiales"
            ]
        }

    # === Fallback
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

        print(f"Current state for {user_id}: {get_user_state(user_id)}")

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
