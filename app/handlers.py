from enum import Enum
from app.db import get_user_state, set_user_state
from utils import extract_concepts, query_weaviate, match_category
from difflib import get_close_matches

MAIN_OPTIONS = [
    "Catálogo de Productos 💊",
    "Ayuda Personalizada de Suplementos 💡",
    "Dudas sobre mis pedidos 📦",
    "Promociones especiales 💸"
]

# === Enum for Chat Stages ===
class ChatStage(Enum):
    WELCOME = "welcome"
    MAIN_MENU = "main_menu"
    RECOMMENDATION = "recommendation_category"
    PERSONAL_ADVICE = "personal_advice"
    ASK_MEDICAL = "ask_medical"
    ASK_PREFERENCE = "ask_preference"
    CUSTOM_QUERY = "custom_query"
    OUTSIDE_STAGE = "outside_stage"
    DONE = "done"

def process_user_input(user_id, user_message):
    state = get_user_state(user_id) or {"stage": ChatStage.WELCOME.value, "context":{}}
    stage = state["stage"] 

    # Initial trigger
    if user_message == "__init__":
        return handle_init(user_id, state)
    
    return route_message(user_id, user_message, state)

def route_message(user_id, user_message, state):
    stage = state["stage"]

    match stage:
        case ChatStage.WELCOME.value:
            return handle_welcome(user_id, user_message, state)
        case ChatStage.MAIN_MENU.value:
            return handle_main_menu(user_id, user_message, state)
        case ChatStage.RECOMMENDATION.value:
            return handle_recommendation(user_id, user_message, state)
        case ChatStage.PERSONAL_ADVICE.value:
            return handle_personal_advice(user_id, user_message, state)
        case ChatStage.ASK_MEDICAL.value:
            return handle_medical(user_id, user_message, state)
        case ChatStage.ASK_PREFERENCE.value:
            return handle_preference(user_id, user_message, state)
        case ChatStage.CUSTOM_QUERY.value:
            return handle_custom_query(user_id, user_message, state)
        case ChatStage.OUTSIDE_STAGE.value:
            return handle_outside(user_id, user_message, state)
        case ChatStage.DONE.value:
            return handle_done(user_id, user_message, state)
        case _:
            return fallback_response()
        

def handle_welcome(user_id, user_message, state):
    state["stage"] = ChatStage.MAIN_MENU.value
    set_user_state(user_id, state)

    return {
        "text": "(WELCOME) 👋 ¡Hola! Soy tu asistente de salud de Xtravit. ¿Qué deseas hacer hoy?",
        "options": [
            "Catálogo de Productos 💊",
            "Ayuda Personalizada de Suplementos 💡",
            "Dudas sobre mis pedidos 📦",
            "Promociones especiales 💸"
        ]
    }

def handle_main_menu(user_id, user_message, state):
    message = user_message.lower().strip()

    match message:
        case msg if "catálogo" in msg or "recomendados" in msg:
            state["stage"] = ChatStage.RECOMMENDATION.value
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
        
        case msg if "personalizada" in msg:
            state["stage"] = ChatStage.PERSONAL_ADVICE.value
            set_user_state(user_id, state)

            return {
                "text": "Para darte las mejores recomendaciones, ¿cuál es tu objetivo principal de salud?"
            }
        
        case msg if "pedidos" in msg:
            return {
                "text": "¿En qué puedo ayudarte con tu pedido?",
                "options": [
                    "Estado de mi pedido", "Información de envío", "Devoluciones", "Métodos de pago"
                ]
            }

        case msg if "promociones" in msg:
            return {
                "text": "¡Excelente! ¿Te interesa recibir un cupón o ver productos en oferta?",
                "options": ["Sí, quiero un cupón", "Ver productos en oferta"]
            }

        case _:
            return handle_outside(user_id, user_message, state)
        
def handle_personal_advice(user_id, user_message, state):
    state["stage"] = ChatStage.ASK_MEDICAL.value
    set_user_state(user_id, state)
    return {
        "text": "Para darte las mejores recomendaciones, ¿cuál es tu objetivo principal de salud?"
    }

def handle_medical(user_id, user_message, state):
    ctx = state.get("context", {})
    ctx["medical"] = user_message
    state["context"] = ctx
    state["stage"] = ChatStage.ASK_PREFERENCE.value
    set_user_state(user_id, state)

    return {
        "text": "¿Tienes alguna preferencia en el tipo de suplemento (vitaminas, minerales, hierbas)?"
    }

def handle_preference(user_id, user_message, state):
    ctx = state.get("context", {})
    ctx["preference"] = user_message
    state["context"] = ctx
    query_terms = [ctx["health_goal"], ctx["preference"]]
    results = query_weaviate(query_terms)
    state["stage"] = ChatStage.DONE.value
    set_user_state(user_id, state)
    return {
        "text": "Gracias por la información. Aquí tienes productos que podrían ayudarte:",
        "products": results
    }

def handle_custom_query(user_id, user_message, state):
    state["stage"] = ChatStage.DONE.value
    set_user_state(user_id, state)
    concepts = extract_concepts(user_message.lower())
    results = query_weaviate(concepts)
    return {
    "text": "Aquí tienes recomendaciones personalizadas:",
    "products": results
    }

def handle_outside(user_id, user_message, state):
    ctx = state.get("context", {})
    out_counter = ctx.get("out_counter", 0)

    # ✅ Normalize and check for close matches
    match = get_close_matches(user_message.strip().lower(), [opt.lower() for opt in MAIN_OPTIONS], n=1, cutoff=0.8)
    if match:
        # If a close match is found, simulate user selected that exact option
        selected = next(opt for opt in MAIN_OPTIONS if opt.lower() == match[0])
        ctx["out_counter"] = 0
        state["context"] = ctx
        set_user_state(user_id, state)
        return route_message(user_id, selected, state)  # Re-route to simulate valid option selected

    # ❌ Still not understood — increment counter
    if out_counter < 2:
        ctx["out_counter"] = out_counter + 1
        state["context"] = ctx
        set_user_state(user_id, state)
        return {
            "text": "Por favor, escoge una de las siguientes opciones 👇",
            "options": MAIN_OPTIONS
        }
    
    # ❗ Final fallback
    ctx["out_counter"] = 0
    state["context"] = ctx
    set_user_state(user_id, state)
    concepts = extract_concepts(user_message.lower())
    results = query_weaviate(concepts)
    return {
        "text": "Gracias por compartir. Aquí tienes algunas recomendaciones:",
        "products": results
    }

    
def handle_done(user_id, state):
    state["stage"] = ChatStage.MAIN_MENU.value
    set_user_state(user_id, state)
    return {
        "text": "(DONE) ¿Te puedo ayudar con algo más?",
        "options": [
            "Catálogo de Productos 💊",
            "Ayuda Personalizada de Suplementos 💡",
            "Dudas sobre mis pedidos 📦",
            "Promociones especiales 💸"
        ]
    }

def handle_init(user_id, state):
    state["stage"] = ChatStage.MAIN_MENU.value
    state["context"] = {}
    set_user_state(user_id, state)
    return {
        "text": "(INIT)👋 ¡Hola! Soy tu asistente de salud de Xtravit. ¿Qué deseas hacer hoy?",
        "options": [
            "Catálogo de Productos 💊",
            "Ayuda Personalizada de Suplementos 💡",
            "Dudas sobre mis pedidos 📦",
            "Promociones especiales 💸"
        ]
    }

def fallback_response():
    return {
        "text": "Lo siento, no entendí eso. ¿Puedes intentarlo de otra forma?"
    }

def handle_recommendation(user_id, user_message, state):
    category_map = {
        "articular": ["articulaciones", "movilidad", "huesos", "músculos"],
        "hombres": ["testosterona", "masculinidad", "prostata", "impulso sexual", "esperma", "urinario"], 
        "higado": ["hígado", "hepáticos", "renal"], 
        "sueño": ["sueño", "melatonina", "relajación", "dormir", "descanso"],
        "energía": ["energía", "fatiga", "vitalidad", "multivitaminas"],
        "digestión": ["digestión", "probióticos", "salud intestinal", "hinchazón", "estómago", "gastrointestinal", "malestar", "barriga", "pipa"],
        "corazón": ["corazón", "presión arterial", "colesterol"],
        "inmunidad": ["inmunidad", "defensas", "sistema inmune"],
        "omega": ["cardiovascular", "cerebral", "ácidos grasos", "EPA", "DHA"],
        "otro": []
    }

    matched_keywords, matched_category = match_category(user_message, category_map)

    if matched_keywords:
        results = query_weaviate(matched_keywords)
        state["stage"] = ChatStage.DONE.value
        set_user_state(user_id, state)
        return {
            "text": f"Aquí tienes algunas recomendaciones para {matched_category}:",
            "products": results
        }
    else:
        return {
            "text": "No entendí esa categoría. ¿Puedes escoger una de las siguientes?",
            "options": list(category_map.keys())
        }
