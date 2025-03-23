from dotenv import load_dotenv
import os
import unittest
import requests
import weaviate
from weaviate.classes.init import Auth
from app.client import get_weaviate_client

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
        requests.post(f"{self.BASE_URL}/items", json=self.item)
        response = requests.put(f"{self.BASE_URL}/items", json={"precio": 12.99})
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
