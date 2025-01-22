from app.client import client

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

client.close()
