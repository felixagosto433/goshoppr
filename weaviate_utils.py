import weaviate

# Connect to Weaviate
client = weaviate.Client("http://localhost:8080")  # Update with your endpoint

def search_supplements(concept):
    """
    Searches the 'Supplements' collection in Weaviate for a given concept.
    """
    query = {
        "Explore": {
            "Supplements": {
                "nearText": {
                    "concepts": [concept]
                }
            }
        }
    }
    try:
        response = client.query.raw(query)
        return response["data"]["Explore"]["Supplements"]
    except Exception as e:
        print(f"Error querying Weaviate: {e}")
        return []
