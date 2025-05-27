from dotenv import load_dotenv
import os
import unittest
import requests
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import Filter
from app.client import get_weaviate_client
import json

# Load the .env.staging file
load_dotenv(".env.staging")

class StagingRoutesTestCase(unittest.TestCase):
    BASE_URL = "https://staging-goshoppr-bcf178c9dd3f.herokuapp.com/"

    def setUp(self):
        self.client = get_weaviate_client()
        self.item = {  
            "nombre": "Test Item",
            "precio": 10.99,
            "inventario": 100,
            "categoria": "Test Category",
            "descripcion": "This is a test item.",
            "ingredientes": ["Test Ingredient"],
            "allergens": ["None"],
            "usage": "Test usage instructions.",
            "recommended_for": ["Test Use"],
            "link": "https://example.com/test-item"
        }

        try:

            client = get_weaviate_client()
            # Check if the "Supplements" collection exists
            collections = client.collections.list_all()
            print(f"Existing collections: {collections.keys()}") 

            if "Supplements" in collections:
                print("Collection 'Supplements' already exists...")
            else:
                print("No Collection found")
                print("Creating 'Supplements' collection...")
                client.collections.create(
                    "Supplements",
                    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
                    properties=[
                Property(name="nombre", data_type=DataType.TEXT),
                Property(name="categoria", data_type=DataType.TEXT),
                Property(name="descripcion", data_type=DataType.TEXT),
                Property(name="ingredientes", data_type=DataType.TEXT_ARRAY),
                Property(name="usage", data_type=DataType.TEXT, vectorizer_config={"skip": True}),
                Property(name="precio", data_type=DataType.NUMBER, vectorizer_config={"skip": True}),
                Property(name="inventario", data_type=DataType.NUMBER, vectorizer_config={"skip": True}),
                Property(name="link", data_type=DataType.TEXT, vectorizer_config={"skip": True}),
            ],
                )
                print("Collection created successfully!!!")

            # Load the collection
            supplements_collection = client.collections.get("Supplements")

            existing_data = supplements_collection.query.fetch_objects(limit=1)
            if not existing_data.objects:
                print("Populating 'Supplements' with vitaminas.json...")
                with open("vitaminas.json", "r", encoding="utf-8") as file:
                    data = json.load(file)

                for obj in data:
                    supplements_collection.data.insert(obj)
                    print(f"Inserted object {obj['nombre']}")

                print("Data imported successfully!")
            else:
                print("Collection already has data.")

        except Exception as e:
            print(f"The following error occurred: {e}")

        
    def tearDown(self):
        """Close Weaviate connection after all tests"""
        if self.client.is_connected():
            self.client.close()
            

    def test_chat_route(self):
        payload = {"message": "Ayuda para dormir"}
        response = requests.post(f"{self.BASE_URL}/chat", json=payload)
        print("DEBUG: Response Status Code:", response.status_code)
        print("DEBUG: Response Text:", response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertTrue(len(response.json()["response"]) > 0)

    def test_get_item_by_name(self):
        response = requests.get(f"{self.BASE_URL}/items", params={"name": "Test Item"})
        print("DEBUG: Response JSON:", response.json())

        self.assertEqual(response.status_code, 200)

    def test_add_item_with_missing_fields(self):
        incomplete_item = {"nombre": "Item incompleto", "precio": "12.99"}
        response = requests.post(f"{self.BASE_URL}/items", json=incomplete_item)
        response_json = response.json()
        print("DEBUG: Response JSON:", response_json)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response_json)
        self.assertTrue(isinstance(response_json["error"], str))

    def test_update_item(self):
        # Checking if the Test Item already exists. 
        response = requests.get(f"{self.BASE_URL}/items", params={"name": "Test Item"})
        if response.status_code == 200 and response.json():
            print("Item already exists! Continuing with test...")
        else:
            requests.post(f"{self.BASE_URL}/items", json=self.item)
            
        response = requests.put(f"{self.BASE_URL}/items/Test Item", json={"precio": 12.99})
        print("DEBUG: Response Status Code after updating:", response.status_code)

        response = requests.get(f"{self.BASE_URL}/items", params={"name": "Test Item"})
        print("DEBUG: Response JSON:", response.json())

        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        if isinstance(json_response, list) and len(json_response) > 0:
            self.assertEqual(json_response[0]["precio"], 12.99)
        else:
            raise AssertionError("Response did not return a list or was empty.")

    def test_delete_item(self):
        response = requests.delete(f"{self.BASE_URL}/items/Test Item")
        print("DEBUG: Response Status Code:", response.status_code)

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_delete_non_existing_item(self):
        response = requests.delete(f"{self.BASE_URL}/items/NonExistingItem")
        print("DEBUG: Response Status Code:", response.status_code)

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

if __name__ == '__main__':
    unittest.main()
