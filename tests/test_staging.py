import unittest
import requests

class StagingRoutesTestCase(unittest.TestCase):
    BASE_URL = "https://staging-goshoppr-bcf178c9dd3f.herokuapp.com/"

    def setUp(self):
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

    def test_chat_route(self):
        payload = {"message": "Ayuda para dormir"}
        response = requests.post(f"{self.BASE_URL}/chat", json=payload)
        print("test_chat_route")
        print("DEBUG: Response Status Code:", response.status_code)
        print("DEBUG: Response Text:", response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertTrue(len(response.json()["response"]) > 0)

    def test_get_item_by_name(self):
        response = requests.get(f"{self.BASE_URL}/items", params={"name": "Test Item"})
        print("test_get_item_by_name")
        print("DEBUG: Response Status Code:", response.status_code)
        print("DEBUG: Response Text:", response.text)
        self.assertEqual(response.status_code, 200)

    def test_add_item_with_missing_fields(self):
        incomplete_item = {"nombre": "Item incompleto", "precio": "12.99"}
        response = requests.post(f"{self.BASE_URL}/items", json=incomplete_item)
        print("test_add_item_with_missing_fields")
        print("DEBUG: Response Status Code:", response.status_code)
        print("DEBUG: Response Text:", response.text)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_update_item(self):
        # Add the test item first
        requests.post(f"{self.BASE_URL}/items", json = self.item)
        # Update the existing field
        response = requests.put(f"{self.BASE_URL}/items/Test Item", json={"precio": 12.99})
        self.assertEqual(response.status_code, 200)
        print("test_update_item")
        print("DEBUG: Response Status Code after updating:", response.status_code)
        print("DEBUG: Response Text:", response.text)

        # Verify the update
        response = requests.get(f"{self.BASE_URL}/items/Test Item", params={"name": "Test Item"})

        print("DEBUG: Response Status Code verification:", response.status_code)
        print("DEBUG: Response Text:", response.text)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["precio"], 12.99)

    def test_delete_item(self):
        response = requests.delete(f"{self.BASE_URL}/items/Test Item")
        print("test_delete_item")
        print("DEBUG: Response Status Code:", response.status_code)
        print("DEBUG: Response Text:", response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "Item deleted successfully!")

    def test_delete_non_existing_item(self):
        response = requests.delete(f"{self.BASE_URL}/items/NonExistingItem")
        print("test_delete_non_existing_item")
        print("DEBUG: Response Status Code:", response.status_code)
        print("DEBUG: Response Text:", response.text)

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

if __name__ == '__main__':
    unittest.main()