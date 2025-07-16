from app.client import get_weaviate_client
import unicodedata
import re
from datetime import datetime
from typing import List, Dict, Any, Union
import os
from dotenv import load_dotenv
import requests

load_dotenv(".env.staging")

HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
API_URL = "https://api-inference.huggingface.co/models/joeddav/xlm-roberta-large-xnli"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

def query_classifier(text: str, labels: List[str]) -> Dict[str, Any]:
    """
    Query the Hugging Face model through their Inference API
    """
    try:
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": labels},
        }
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"❌ Error querying classifier: {str(e)}")
        return {"labels": labels, "scores": [1.0/len(labels)] * len(labels)}

def normalize_text(text: str) -> str:
    """Normalize text by removing accents and special characters."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s]", "", text)  # remove non-word symbols
    return text.lower().strip()

def append_history(state: Dict[str, Any], sender: str, message: str) -> None:
    """Append a message to the conversation history."""
    history = state.get("history", [])
    # Limit history to last 100 messages to prevent memory issues
    if len(history) >= 100:
        history = history[-99:]
    
    history.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": sender,
        "message": message,
        "stage": state.get("stage", "unknown")
    })
    state["history"] = history

def query_weaviate(concepts: Union[str, List[str]], client_instance: Any) -> List[Dict[str, Any]]:
    """
    Query Weaviate database for supplements matching given concepts.
    
    Args:
        concepts: String or list of strings to search for
        client_instance: Weaviate client instance
    
    Returns:
        List of matching supplement dictionaries
    """
    try:
        if not client_instance:
            print("❌ Error: No Weaviate client provided")
            return []
            
        if isinstance(concepts, str):
            concepts = [concepts]
            
        collection = client_instance.collections.get("Supplements")
        response = collection.query.near_text(
            query = concepts,
            limit = 2
        )

        if response and response.objects:
            return [
                {
                    "image": obj.properties.get("image"),
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
    
def match_category(message: str, category_list: Dict[str, List[str]]) -> List[str]:
    """
    Match a message to a category and return associated keywords.
    
    Args:
        message: User message to categorize
        category_list: Dictionary mapping categories to lists of keywords
    
    Returns:
        List of keywords associated with the matched category
    """
    if not message or not category_list:
        return []
        
    results = query_classifier(message, list(category_list.keys()))
    category = results["labels"][0]

    return category_list.get(category, [])