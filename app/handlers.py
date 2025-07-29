from enum import Enum
from app.db import get_user_state, set_user_state, get_pueblos, get_pharmacy_address
from utils import query_weaviate, match_category, normalize_text, append_history, get_weaviate_client, query_classifier as classifier
from difflib import get_close_matches
from datetime import datetime
from app.analytics_db import AnalyticsDB, track_product_recommendation

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
    PEDIDO = "pedido"
    RECOMMENDATION = "recommendation_category"
    PERSONAL_ADVICE = "personal_advice"
    ASK_MEDICAL = "ask_medical"
    ASK_PREFERENCE = "ask_preference"
    CUSTOM_QUERY = "custom_query"
    DONE = "done"
    LOCATION = "localizacion"
    PRE_LOCATION = "pre-localizacion"

def process_user_input(user_id, user_message):
    state = get_user_state(user_id) or {"stage": ChatStage.MAIN_MENU.value, "context":{}}

    if "session_start" not in state.get("context", {}):
        state["context"]["session_start"] = datetime.utcnow().isoformat() + "Z"

    # Only create a new session if not already present
    if "session_id" not in state["context"]:
        session_id = AnalyticsDB.create_user_session(user_id)
        state["context"]["session_id"] = session_id
    else:
        session_id = state["context"]["session_id"]

    append_history(state, "user", user_message)
    print(f"State at start {state}")
    stage = state["stage"]

    if user_message == "__init__":
        return handle_init(user_id, state)
    return route_message(user_id, user_message, state)

def route_message(user_id, user_message, state):
  stage = state["stage"]

  match stage:
    case ChatStage.MAIN_MENU.value:
        return handle_main_menu(user_id, user_message, state)
    case ChatStage.PEDIDO.value:
        return handle_pedido(user_id, user_message, state)
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
      "text": "👋 ¡Hola! Soy tu asistente de salud de Xtravit. ¿Qué deseas hacer hoy?",
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
        state["stage"] = ChatStage.PEDIDO.value
        set_user_state(user_id, state)
        
        response = {
            "text": "¿En qué puedo ayudarte con tu pedido?",
            "options": ["Estado del pedido", "Cambios y devoluciones"]
        }
        append_history(state, "bot", response["text"])
        return response

    # FOR ADDING OTHER OPTIONS!
    # elif "promociones" in selected.lower():
    #     state["stage"] = ChatStage.DONE.value
    #     set_user_state(user_id, state)
        
    #     response = {
    #         "text": "¡Excelente! ¿Te gustaría recibir un cupón o ver productos en oferta?",
    #         "options": ["Sí, quiero un cupón", "Ver productos en oferta"]
    #     }
    #     append_history(state, "bot", response["text"])
    #     return response

  return {
      "text": "Lo siento, no entendí tu selección. Por favor escoge una opción:",
      "options": MAIN_OPTIONS
  }

def handle_pedido(user_id, user_message, state):
    clean_message = normalize_text(user_message)
    # You can use a classifier or just check for keywords
    if "cambio" in clean_message or "devolucion" in clean_message or "devolución" in clean_message:
        return handle_pedidos(user_id, user_message, state)
    elif "estado" in clean_message:
        # Implement a handler for order status if you want
        return {
            "text": "Para consultar el estado de tu pedido, por favor proporciona tu número de pedido o revisa tu correo de confirmación."
        }
    else:
        return {
            "text": "¿Sobre qué aspecto de tu pedido necesitas ayuda?",
            "options": ["Estado del pedido", "Cambios y devoluciones"]
        }
    
def handle_pedidos(user_id, user_message, state):
    ctx = state.setdefault("context", {})
    state["stage"] = ChatStage.DONE.value
    state["context"] = ctx
    set_user_state(user_id, state)
    print(f"🧠 New stage set to: {state['stage']}")
    response = {
        "messages": [
            "<h3>📦 <b>Envíos</b></h3>🚚 Cobertura: Solo realizamos envíos dentro de Puerto Rico (no internacionales).<br>⏱️ Los pedidos se procesan en 1-2 días hábiles desde la confirmación.<br>📅 Pedidos en fines de semana o feriados se procesan el siguiente día hábil.",
            "<h3>🔄 <b>Devoluciones, Reembolsos y Cambios</b></h3>✅ Puedes devolver productos dentro de los 30 días posteriores a la entrega, siempre que estén sin abrir y sin usar.<br>📧 <b>Cómo devolver:</b> 1. Escribe a nuestro equipo con tu número de pedido y motivo. 2. Recibirás una etiqueta e instrucciones. 3. Empaca el producto y envíalo con la etiqueta proporcionada.<br>💸 El cliente cubre el envío, salvo error de nuestra parte o producto defectuoso.<br>💳 Reembolsos: Se procesan en 7-10 días hábiles al mismo método de pago.<br>🚫 No aceptamos devoluciones de productos abiertos o usados, productos en promoción, o productos dañados por mal uso o descuento y tarjetas de regalo.",
            "<h3>↔️ <b>No realizamos cambios directos</b></h3>Si deseas un cambio, devuelve el producto siguiendo el proceso anterior y haz un nuevo pedido."
        ]
    }
    append_history(state, "bot", "Información sobre Pedidos, Devoluciones y Cambios enviada.")
    return response
        
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
      "text": "¿Tienes alguna preferencia en el tipo de suplemento (suplementos, vitaminas, minerales, hierbas)?"
  }
  append_history(state, "bot", response["text"])
  return response

def handle_preference(user_id, user_message, state):
    ctx = state.setdefault("context", {})
    ctx["preference"] = normalize_text(user_message)
    state["context"] = ctx
    # When using it later
    session_id = state["context"].get("session_id")
    query_terms = [ctx["health_goal"], ctx["preference"]]
    # Get Weaviate client and query
    client = get_weaviate_client()
    results = query_weaviate(query_terms, client)
    state["stage"] = ChatStage.PRE_LOCATION.value

    AnalyticsDB.save_user_goals(
      user_id=user_id,
      session_id=session_id,
      health_goal=ctx.get("health_goal"),
      medical_condition=ctx.get("medical"),
      supplement_preference=ctx.get("preference"),
      pueblo=ctx.get("pueblo")
      )

    track_product_recommendation(
      user_id=user_id,
      session_id=session_id,
      products=results,
      stage=state["stage"],
      context=state.get("context")
      )
    
    set_user_state(user_id, state)
    print(f"🧠 New stage set to: {state['stage']}")
    response = {
        "text": f"Aquí tienes algunas recomendaciones:",
        "products": results,
        "followup_text": "¿Deseas que busquemos las farmacias más cercanas donde puedes conseguir nuestros productos?",
        "options": ["Si", "No"]
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
            "text": "Por favor, describe específicamente lo que estás buscando mejorar:"
        }
        append_history(state, "bot", response["text"])
        return response

    classification = classifier(clean_message, recomendations)
    match = classification["labels"][0]
    selected = next((opt for opt in recomendations if opt.lower() == match.lower()), None)
    
    # Get Weaviate client and query
    client = get_weaviate_client()
    results = query_weaviate(selected, client)
    print("DEBUG PRODUCTS:", results)

    session_id = state["context"].get("session_id")

    track_product_recommendation(
      user_id=user_id,
      session_id=session_id,
      products=results,
      stage=state["stage"],
      context=state.get("context")
      )
    
    state["stage"] = ChatStage.PRE_LOCATION.value
    set_user_state(user_id, state)
    print(f"🧠 New stage set to: {state['stage']}")
    
    response = {
        "text": f"Aquí tienes algunas recomendaciones para {selected}:",
        "products": results,
        "followup_text": "¿Deseas que busquemos las farmacias más cercanas donde puedes conseguir nuestros productos?",
        "options": ["Si", "No"]
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
    session_id = state["context"].get("session_id")
    track_product_recommendation(
      user_id=user_id,
      session_id=session_id,
      products=results,
      stage=state["stage"],
      context=state.get("context")
      )

    state["stage"] = ChatStage.PRE_LOCATION.value
    set_user_state(user_id, state)
    print(f"🧠 New stage set to: {state['stage']}")

    response = {
        "text": "Aquí tienes recomendaciones personalizadas:",
        "products": results,
        "followup_text": "¿Deseas que busquemos las farmacias más cercanas donde puedes conseguir nuestros productos?",
        "options": ["Si", "No"]
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
   set_user_state(user_id, state)

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

   AnalyticsDB.track_location_search(
      pueblo=matched_pueblo,
      pharmacy_name=pharmacy_info[0]["name"] if pharmacy_info else None,
      successful=bool(pharmacy_info)
  )
   
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
  session_id = state["context"].get("session_id")

  response = {
    "text": "¿Te puedo ayudar con algo más?",
    "options": MAIN_OPTIONS
  }
  append_history(state, "bot", response["text"])
  AnalyticsDB.update_session_end(session_id)
  return response



def fallback_response():
    response = {
        "text": "Lo siento, no entendí tu mensaje. Por favor, intenta de nuevo."
    }
    return response
