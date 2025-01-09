import unittest
import requests

class ProductionRoutesTestCase(unittest.TestCase):
    BASE_URL = "https://vast-escarpment-05453-5a02b964d113.herokuapp.com/" 

    def setUp(self):
        self.test_item = {
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

    def test_get_item_by_name(self):
        response = requests.get(f"{self.BASE_URL}/items", params={"name": "Test Item"})
        self.assertEqual(response.status_code, 200)

    def test_add_item_missing_fields(self):
        incomplete_item = {"nombre": "Incomplete Item", "precio": 5.99}
        response = requests.post(f"{self.BASE_URL}/items", json=incomplete_item)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_update_item(self):
        # Add the test item first
        requests.post(f"{self.BASE_URL}/items", json=self.test_item)

        # Update the test item
        updated_data = {"precio": 12.99}
        response = requests.put(f"{self.BASE_URL}/items/Test Item", json=updated_data)
        self.assertEqual(response.status_code, 200)

        # Verify the update
        response = requests.get(f"{self.BASE_URL}/items", params={"name": "Test Item"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["precio"], 12.99)

    def test_delete_item(self):
        response = requests.delete(f"{self.BASE_URL}/items/Test Item")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "Item deleted successfully!")

    def test_delete_non_existing_item(self):
        response = requests.delete(f"{self.BASE_URL}/items/NonExistingItem")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

if __name__ == '__main__':
    unittest.main()
