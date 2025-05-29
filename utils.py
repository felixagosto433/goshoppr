from app.client import get_weaviate_client
import difflib

def query_weaviate(concepts):
    try:
        client = get_weaviate_client()
        collection = client.collections.get("Supplements")
        response = collection.query.near_text(
            query = concepts,
            limit = 3
        )

        if response and response.objects:
            return [
                {
                    "name": obj.properties.get("nombre"),
                    "description": obj.properties.get("descripcion"),
                    "price": obj.properties.get("precio"),
                    "category": obj.properties.get("categoria"),
                    "link": obj.properties.get("link"),
                    "usage": obj.properties.get("usage"),
                    "recommended_for": obj.properties.get("recommended_for"),
                    "allergens": obj.properties.get("allergens")
                }
                for obj in response.objects

            ]
        
        return [] # No objects found
    
    except Exception as e:
        print(f"❌ Error in query_weaviate: {str(e)}")
        return []
    
def match_category(user_message, category_map, cutoff=0.7):
    message = user_message.lower()
    matched_keywords = []
    matched_category = None

    # First try exact substring match
    for key, val in category_map.items():
        if key in message or any(c in message for c in val):
            matched_keywords.extend(val)
            matched_category = key
            print(f"🟢 Matched by substring: {key}")
            return matched_keywords, matched_category

    # Fallback: fuzzy match the entire user message to category names
    possible_categories = list(category_map.keys())
    close_matches = difflib.get_close_matches(message, possible_categories, n=1, cutoff=cutoff)
    if close_matches:
        matched_category = close_matches[0]
        matched_keywords = category_map[matched_category]
        print(f"🔍 Fuzzy matched category: {matched_category}")
        return matched_keywords, matched_category

    print("⚠️ No match found")
    return [], None

def extract_concepts(user_message):
    message = user_message.lower()

    keyword_map = {
        "articular": ["articulaciones", "movilidad", "huesos", "músculos"],
        "hombres": ["testosterona", "masculinidad", "prostata", "impulso sexual", "esperma", "urinario"], 
        "higado": ["hígado", "hepáticos", "renal"], 
        "sueño": ["sueño", "melatonina", "relajación", "dormir", "descanso"],
        "energía": ["energía", "fatiga", "vitalidad", "multivitaminas"],
        "digestión": ["digestión", "probióticos", "salud intestinal", "hinchazón", "estómago", "gastrointestinal", "malestar"],
        "corazón": ["corazón", "presión arterial", "colesterol"],
        "inmunidad": ["inmunidad", "defensas", "sistema inmune"],
        "omega": ["cardiovascular", "cerebral", "ácidos grasos", "EPA", "DHA"],
    }

    matched_concepts = []

    for keyword, concepts in keyword_map.items():
        if keyword in message or any(c in message for c in concepts):
            matched_concepts.extend(concepts)

    if matched_concepts:
        return list(set(matched_concepts))  # remove duplicates

    return [user_message]