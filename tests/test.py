import unittest
from flask import Flask
from app import create_app, db  # Import your app factory function and database instance
from weaviate.util import generate_uuid5
from config import TestingConfig

class FlaskRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_class=TestingConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()  # Initialize the database

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

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()  # Clean up the database after tests

    # TEST GET ITEM
    def test_get_item_by_name(self):
        """
        Test fetching a single item by name (GET /items?name=...).
        """
        response = self.client.get('/items', query_string={"name": "Test Item"})
        self.assertEqual(response.status_code, 200)

    # TEST POST ITEM (ADD ITEM)
    def test_add_item_missing_fields(self):
        """
        Test adding a new item (POST /items).
        """
        incomplete_item = {"nombre": "Incomplete Item", "precio": 5.99}
        response = self.client.post('/items', json=incomplete_item)
        self.assertAlmostEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    # TEST PUT ROUTE
    def test_update_item(self):
        """
        Test updating an existing item (PUT /items/<string:name>).
        """
        # Add the test item first
        response = self.client.post('/items', json=self.test_item)
        self.assertEqual(response.status_code, 201)
        
        # Update the test item
        updated_data = {"precio": 12.99}
        response = self.client.put('/items/Test Item', json=updated_data)
        
        # Verify the update by fetching the item
        response = self.client.get('/items', query_string={"name": "Test Item"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["precio"], 12.99)

    # TEST DELETE ROUTE
    def test_delete_item(self):
        """
        Test deleting an existing item (DELETE /items/<string:name>).
        """
        response = self.client.delete('/items/Test Item')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Item deleted successfully!")

    def test_delete_non_existing_item(self):
        """
        Test deleting a non-existing item (DELETE /items/<string:name>).
        """
        response = self.client.delete('/items/NonExistingItem')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

if __name__ == '__main__':
    unittest.main()