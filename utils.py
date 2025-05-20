from app.client import get_weaviate_client

def query_weaviate(concepts):
    try:
        client = get_weaviate_client()
        collection = client.collections.get("Supplements")
        response = collection.query.near_text(
            query = concepts,
            limit = 5
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

def extract_concepts(user_message):
    message = user_message.lower()

    keyword_map = {
        "sueño": ["sueño", "melatonina", "relajación", "dormir"],
        "ansiedad": ["ansiedad", "estrés", "calmante", "nervios"],
        "energía": ["energía", "fatiga", "vitalidad", "multivitaminas"],
        "digestión": ["digestión", "probióticos", "salud intestinal", "hinchazón", "estómago"],
        "corazón": ["corazón", "presión arterial", "colesterol"],
        "inmunidad": ["inmunidad", "defensas", "sistema inmune"]
    }

    for keyword, concepts in keyword_map.items():
        if keyword in message:
            return concepts

    # fallback: just return what the user typed as one concept
    return [user_message]

client.close()
