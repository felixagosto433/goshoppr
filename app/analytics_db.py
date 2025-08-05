import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

load_dotenv(".env.staging")

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
conn.autocommit = True
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

class AnalyticsDB:
    """Enhanced database functions for analytics dashboard"""
    
    @staticmethod
    def create_user_session(user_id: str, session_start: datetime = None) -> int:
        """Create a new user session and return session_id"""
        if session_start is None:
            session_start = datetime.utcnow()
            
        cursor.execute("""
            INSERT INTO user_sessions (user_id, session_start)
            VALUES (%s, %s)
            RETURNING id
        """, (user_id, session_start))
        
        session_id = cursor.fetchone()[0]
        return session_id
    
    @staticmethod
    def update_session_end(session_id: int, session_end: datetime = None):
        """Update session end time and calculate duration"""
        if session_end is None:
            session_end = datetime.utcnow()
            
        cursor.execute("""
            UPDATE user_sessions 
            SET session_end = %s, completed_journey = TRUE
            WHERE id = %s
        """, (session_end, session_id))
    
    @staticmethod
    def track_product_interaction(
        user_id: str,
        session_id: int,
        product_name: str,
        product_category: str,
        stage: str,
        user_goal: str = None,
        user_preference: str = None
    ):
        """Track product interactions for analytics"""
        cursor.execute("""
            INSERT INTO product_interactions (
                user_id, session_id, product_name, product_category, stage, user_goal, user_preference
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, session_id, product_name, product_category, stage, user_goal, user_preference
        ))
    
    @staticmethod
    def save_user_goals(
        user_id: str,
        session_id: int,
        health_goal: str,
        medical_condition: str = None,
        supplement_preference: str = None,
        pueblo: str = None
    ):
        """Save user health goals and preferences"""
        cursor.execute("""
            INSERT INTO user_goals (
                user_id, session_id, health_goal, medical_condition,
                supplement_preference, pueblo
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id, session_id, health_goal, medical_condition,
            supplement_preference, pueblo
        ))
    
    @staticmethod
    def track_location_search(pueblo: str, pharmacy_name: str = None, successful: bool = True):
        """Track location searches for analytics (logs every interaction with timestamp)"""
        cursor.execute("""
            INSERT INTO location_analytics (
                pueblo, pharmacy_name, last_searched, interaction_time
            ) VALUES (%s, %s, %s, %s)
        """, (
            pueblo, pharmacy_name,
            1 if successful else 0,
            datetime.utcnow()
        ))

# Enhanced database functions that integrate with existing code
def enhanced_set_user_state(user_id: str, state: Dict[str, Any], session_id: int = None):
    """Enhanced version of set_user_state that also tracks analytics"""
    from app.db import set_user_state
    
    # Call original function
    set_user_state(user_id, state)
    
    # Track analytics if session_id is provided
    if session_id and "context" in state:
        context = state["context"]
        
        # Track user goals if available
        if "health_goal" in context:
            AnalyticsDB.save_user_goals(
                user_id=user_id,
                session_id=session_id,
                health_goal=context.get("health_goal"),
                medical_condition=context.get("medical"),
                supplement_preference=context.get("preference"),
                pueblo=context.get("Pueblo")
            )
        
        # Track location search if available
        if "Pueblo" in context:
            AnalyticsDB.track_location_search(
                pueblo=context["Pueblo"],
                successful=True
            )

def track_product_recommendation(user_id: str, session_id: int, products: List[Dict], stage: str, context: Dict = None):
    """Track product recommendations for analytics"""
    for product in products:
        AnalyticsDB.track_product_interaction(
            user_id=user_id,
            session_id=session_id,
            product_name=product.get("name", "Unknown"),
            product_category=product.get("category", "Unknown"),
            stage=stage,
            user_goal=context.get("health_goal") if context else None,
            user_preference=context.get("preference") if context else None
        ) 