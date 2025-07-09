from enum import Enum
from app.db import get_user_state, set_user_state, get_pueblos, get_pharmacy_address
from utils import query_weaviate, match_category, normalize_text, append_history, get_weaviate_client, query_classifier as classifier
from difflib import get_close_matches
from datetime import datetime

MAIN_OPTIONS = [
    "Catálogo de Productos",
    "Ayuda Personalizada de Suplementos",
    "Dudas sobre mis pedidos",
    "Promociones especiales"
]

REC_OPTIONS = [
    "Energía y Vitalidad", 
    "Sueño y Relajación", 
    "Salud del Corazón",
    "Apoyo Immune", 
    "Salud Digestiva", 
    "Otro (especificar)"
]

cat_subcat = {
    "articular": ["articulaciones", "movilidad", "huesos", "músculos"],
    "masculinidad": ["testosterona", "masculinidad", "prostata", "impulso sexual", "esperma", "urinario"], 
    "descanso": ["sueño", "melatonina", "relajación", "dormir", "descanso"],
    "energía": ["energía", "fatiga", "vitalidad", "multivitaminas"],
    "digestión": ["digestión", "probióticos", "salud intestinal", "hinchazón", "estómago", "gastrointestinal", "malestar"],
    "corazón": ["corazón", "presión arterial", "colesterol"],
    "inmunidad": ["inmunidad", "defensas", "sistema inmune"],
    "ácidos grasos": ["cerebral", "ácidos grasos", "EPA", "DHA"]
}

# === Enum for Chat Stages ===
class ChatStage(Enum):
    WELCOME = "welcome"
    MAIN_MENU = "main_menu"
    RECOMMENDATION = "recommendation_category"
    PERSONAL_ADVICE = "personal_advice"
    ASK_MEDICAL = "ask_medical"
    ASK_PREFERENCE = "ask_preference"
    CUSTOM_QUERY = "custom_query"
    DONE = "done"
    LOCATION = "localizacion"
    PRE_LOCATION = "pre-localizacion"

def process_user_input(user_id, user_message):
  
  # Checks state
  state = get_user_state(user_id) or {"stage": ChatStage.MAIN_MENU.value, "context":{}}

  # Add session_start if not already present
  if "session_start" not in state.get("context", {}):
      state["context"]["session_start"] = datetime.utcnow().isoformat() + "Z"

  append_history(state, "user", user_message)
  print(f"State at start {state}")
  stage = state["stage"] 

  # Initial trigger
  if user_message == "__init__":
      return handle_init(user_id, state)
  # Route message
  return route_message(user_id, user_message, state)

def route_message(user_id, user_message, state):
  stage = state["stage"]

  match stage:
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
    case ChatStage.PRE_LOCATION.value:
        return handle_pre_location(user_id, user_message, state)
    case ChatStage.LOCATION.value:
        return handle_location(user_id, user_message, state)
    case ChatStage.DONE.value:
        return handle_done(user_id, user_message, state)
    case _:
        return fallback_response()

def handle_init(user_id, state):
  state["stage"] = ChatStage.MAIN_MENU.value
  state["context"] = {}
  set_user_state(user_id, state)
  
  response = {
      "text": "(INIT)👋 ¡Hola! Soy tu asistente de salud de Xtravit. ¿Qué deseas hacer hoy?",
      "options": [
          "Catálogo de Productos 💊",
          "Ayuda Personalizada de Suplementos 💡",
          "Dudas sobre mis pedidos 📦",
          "Promociones especiales 💸"
      ]
  }
  append_history(state, "bot", response["text"])
  return response

def handle_main_menu(user_id, user_message, state):
  clean_message = normalize_text(user_message)

  classification = classifier(clean_message, MAIN_OPTIONS)
  match = classification["labels"][0]
  selected = next((opt for opt in MAIN_OPTIONS if opt.lower() == match.lower()), None)

  if selected:
    if "catálogo" in selected.lower():
        state["stage"] = ChatStage.RECOMMENDATION.value
        set_user_state(user_id, state)
        
        response = {
            "text": "¿Qué estás buscando mejorar?",
            "options": REC_OPTIONS
        }
        append_history(state, "bot", response["text"])
        return response

    elif "personalizada" in selected.lower():
        state["stage"] = ChatStage.PERSONAL_ADVICE.value
        set_user_state(user_id, state)
        
        response = {
            "text": "¿Cuál es tu objetivo principal de salud?"
        }
        append_history(state, "bot", response["text"])
        return response

    elif "pedidos" in selected.lower():
        state["stage"] = ChatStage.DONE.value
        set_user_state(user_id, state)
        
        response = {
            "text": "¿En qué puedo ayudarte con tu pedido?",
            "options": ["Estado del pedido", "Métodos de pago", "Cambios y devoluciones"]
        }
        append_history(state, "bot", response["text"])
        return response

    elif "promociones" in selected.lower():
        state["stage"] = ChatStage.DONE.value
        set_user_state(user_id, state)
        
        response = {
            "text": "¡Excelente! ¿Te gustaría recibir un cupón o ver productos en oferta?",
            "options": ["Sí, quiero un cupón", "Ver productos en oferta"]
        }
        append_history(state, "bot", response["text"])
        return response

  return {
      "text": "Lo siento, no entendí tu selección. Por favor escoge una opción:",
      "options": MAIN_OPTIONS
  }
        
def handle_personal_advice(user_id, user_message, state):
  # Store initial message
  ctx = state.setdefault("context", {})
  health_goal = normalize_text(user_message)
  if health_goal:
      ctx["health_goal"] = health_goal
      
  state["stage"] = ChatStage.ASK_MEDICAL.value
  state["context"] = ctx
  set_user_state(user_id, state)
  print(f"🧠 New stage set to: {state['stage']}")
  
  response = {
      "text": "¿Tienes alguna condicion medica?"
  }
  append_history(state, "bot", response["text"])
  return response

def handle_medical(user_id, user_message, state):
  ctx = state.setdefault("context", {})
  ctx["medical"] = normalize_text(user_message)
  state["stage"] = ChatStage.ASK_PREFERENCE.value
  state["context"] = ctx
  set_user_state(user_id, state)
  print(f"🧠 New stage set to: {state['stage']}")
  
  response = {
      "text": "¿Tienes alguna preferencia en el tipo de suplemento (vitaminas, minerales, hierbas)?"
  }
  append_history(state, "bot", response["text"])
  return response

def handle_preference(user_id, user_message, state):
    ctx = state.setdefault("context", {})
    ctx["preference"] = normalize_text(user_message)
    state["context"] = ctx
    query_terms = [ctx["health_goal"], ctx["preference"]]
    # Get Weaviate client and query
    client = get_weaviate_client()
    results = query_weaviate(query_terms, client)
    state["stage"] = ChatStage.PRE_LOCATION.value
    
    set_user_state(user_id, state)
    print(f"🧠 New stage set to: {state['stage']}")
    response = {
        "text": "Gracias por la información. Aquí tienes productos que podrían ayudarte. ¿Desea que busquemos la farmacia mas cercana?",
        "products": results
    }
    append_history(state, "bot", response["text"])
    return response

def handle_recommendation(user_id, user_message, state):
    recomendations = [
        "Energía y Vitalidad", 
        "Sueño y Relajación", 
        "Salud del Corazón",
        "Apoyo Immune", 
        "Salud Digestiva", 
        "Otro (especificar)"
    ]

    clean_message = normalize_text(user_message)

    # Handle Other option
    if any(term in clean_message for term in ["otro", "especificar"]):
        state["stage"] = ChatStage.CUSTOM_QUERY.value
        set_user_state(user_id, state)
        
        response = {
            "text": "(REC) Por favor, describe específicamente lo que estás buscando mejorar:"
        }
        append_history(state, "bot", response["text"])
        return response

    classification = classifier(clean_message, recomendations)
    match = classification["labels"][0]
    selected = next((opt for opt in recomendations if opt.lower() == match.lower()), None)
    
    # Get Weaviate client and query
    client = get_weaviate_client()
    results = query_weaviate(selected, client)
    
    state["stage"] = ChatStage.PRE_LOCATION.value
    set_user_state(user_id, state)
    print(f"🧠 New stage set to: {state['stage']}")
    
    response = {
        "text": f"Aquí tienes algunas recomendaciones para {selected}: ¿Deseas que busquemos las farmacias mas cercanas donde puuedes conseguir nuestros productos?",
        "products": results
    }
    append_history(state, "bot", response["text"])
    return response

def handle_custom_query(user_id, user_message, state):
    clean_message = normalize_text(user_message)
    classification = classifier(clean_message, list(cat_subcat.keys()))
    match = classification["labels"][0]

    # Get Weaviate client and query
    client = get_weaviate_client()
    results = query_weaviate(cat_subcat[match], client)

    state["stage"] = ChatStage.PRE_LOCATION.value
    set_user_state(user_id, state)
    print(f"🧠 New stage set to: {state['stage']}")

    response = {
        "text": "(CUS) Aquí tienes recomendaciones personalizadas:¿Deseas que busquemos las farmacias mas cercanas donde puuedes conseguir nuestros productos?",
        "products": results
    }
    append_history(state, "bot", response["text"])
    return response

def handle_pre_location(user_id, user_message, state):
    ctx = state.setdefault("context", {})
    ctx["pueblo"] = normalize_text(user_message)
    state["context"] = ctx
    if "Si" in user_message:
        state["stage"] = ChatStage.LOCATION.value
        set_user_state(user_id, state)
        response = {
           "text":"¿En que pueblo resides?"
        }
        append_history(state, "bot", response["text"])
        return response
    
    state["stage"] = ChatStage.DONE.value
    set_user_state(user_id, state)
    response = {
        "text": "¡De acuerdo!"
    }
    append_history(state, "bot", response["text"])
    return response
   
def handle_location(user_id, user_message, state):
   # Get the response as to if the want the pharmacies or not. 

   # Query the latest pueblo table
   pueblos = get_pueblos()
   state["stage"] = ChatStage.DONE.value
   clean_message = normalize_text(user_message).upper()
   # Save the Pueblo to the database inside the context.
   state["context"]["Pueblo"] = clean_message.upper()

   # Find the closest matching pueblo
   results = classifier(clean_message, pueblos)
   matched_pueblo = results["labels"][0]
   
   # Get pharmacy information for the matched pueblo
   pharmacy_jsons = get_pharmacy_address(matched_pueblo)

   # Extract pharmacy names and their Google Maps links
   pharmacy_info = []
   for pharmacy in pharmacy_jsons:
      pharmacy_info.append({
         "name": pharmacy["Pharmacy"],
         "maps_link": pharmacy["Location"]
      })

   response = {
      "text": f"Estas son las farmacias más cercanas en {matched_pueblo}:",
      "pharmacies": pharmacy_info
   }
   append_history(state, "bot", response["text"])
   return response

def handle_done(user_id, user_message, state):
  state["stage"] = ChatStage.MAIN_MENU.value
  state["context"]["session_end"] = datetime.utcnow().isoformat() + "Z"
  set_user_state(user_id, state)
  print(f"🧠 New stage set to: {state['stage']}")

  response = {
    "text": "(DONE) ¿Te puedo ayudar con algo más?",
    "options": MAIN_OPTIONS
  }
  append_history(state, "bot", response["text"])
  return response

def fallback_response():
    response = {
        "text": "Lo siento, no entendí tu mensaje. Por favor, intenta de nuevo."
    }
    return response
