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
        interaction_type: str,
        stage: str,
        user_goal: str = None,
        user_preference: str = None
    ):
        """Track product interactions for analytics"""
        cursor.execute("""
            INSERT INTO product_interactions (
                user_id, session_id, product_name, product_category,
                interaction_type, stage, user_goal, user_preference
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, session_id, product_name, product_category,
            interaction_type, stage, user_goal, user_preference
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
        """Track location searches for analytics"""
        cursor.execute("""
            INSERT INTO location_analytics (pueblo, pharmacy_name, total_searches, successful_matches, last_searched)
            VALUES (%s, %s, 1, %s, %s)
            ON CONFLICT (pueblo) DO UPDATE SET
                total_searches = location_analytics.total_searches + 1,
                successful_matches = location_analytics.successful_matches + %s,
                last_searched = EXCLUDED.last_searched
        """, (
            pueblo, pharmacy_name, 
            1 if successful else 0,
            datetime.utcnow(),
            1 if successful else 0
        ))
    
    @staticmethod
    def get_user_engagement_metrics(start_date: str, end_date: str) -> Dict[str, Any]:
        """Get user engagement metrics for dashboard"""
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT user_id) as total_users,
                AVG(session_duration) as avg_session_duration,
                ROUND(COUNT(CASE WHEN completed_journey THEN 1 END) * 100.0 / COUNT(*), 2) as completion_rate,
                COUNT(*) as total_sessions
            FROM user_sessions
            WHERE session_start::DATE BETWEEN %s AND %s
        """, (start_date, end_date))
        
        row = cursor.fetchone()
        return {
            "total_users": row[0] or 0,
            "avg_session_duration": str(row[1]) if row[1] else "00:00:00",
            "completion_rate": float(row[2]) if row[2] else 0.0,
            "total_sessions": row[3] or 0
        }
    
    @staticmethod
    def get_top_health_goals(limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common health goals"""
        cursor.execute("""
            SELECT 
                health_goal,
                COUNT(*) as frequency
            FROM user_goals
            WHERE health_goal IS NOT NULL
            GROUP BY health_goal
            ORDER BY frequency DESC
            LIMIT %s
        """, (limit,))
        
        return [{"goal": row[0], "frequency": row[1]} for row in cursor.fetchall()]
    
    @staticmethod
    def get_product_analytics() -> List[Dict[str, Any]]:
        """Get product recommendation analytics"""
        cursor.execute("""
            SELECT 
                product_name,
                product_category,
                COUNT(*) as total_recommendations,
                COUNT(CASE WHEN interaction_type = 'clicked' THEN 1 END) as clicks,
                ROUND(
                    COUNT(CASE WHEN interaction_type = 'clicked' THEN 1 END) * 100.0 / COUNT(*), 2
                ) as click_rate
            FROM product_interactions
            GROUP BY product_name, product_category
            ORDER BY total_recommendations DESC
        """)
        
        return [{
            "product_name": row[0],
            "category": row[1],
            "total_recommendations": row[2],
            "clicks": row[3],
            "click_rate": float(row[4]) if row[4] else 0.0
        } for row in cursor.fetchall()]
    
    @staticmethod
    def get_location_analytics() -> List[Dict[str, Any]]:
        """Get location search analytics"""
        cursor.execute("""
            SELECT 
                pueblo,
                COUNT(*) as total_searches,
                COUNT(CASE WHEN successful_matches > 0 THEN 1 END) as successful_searches,
                ROUND(
                    COUNT(CASE WHEN successful_matches > 0 THEN 1 END) * 100.0 / COUNT(*), 2
                ) as success_rate
            FROM location_analytics
            GROUP BY pueblo
            ORDER BY total_searches DESC
        """)
        
        return [{
            "pueblo": row[0],
            "total_searches": row[1],
            "successful_searches": row[2],
            "success_rate": float(row[3]) if row[3] else 0.0
        } for row in cursor.fetchall()]
    
    @staticmethod
    def get_user_journey_analytics(limit: int = 50) -> List[Dict[str, Any]]:
        """Get user journey completion analytics"""
        cursor.execute("""
            SELECT 
                us.user_id,
                us.session_start,
                us.session_end,
                us.session_duration,
                us.total_interactions,
                us.completed_journey,
                ug.health_goal,
                ug.medical_condition,
                ug.supplement_preference,
                ug.pueblo
            FROM user_sessions us
            LEFT JOIN user_goals ug ON us.id = ug.session_id
            ORDER BY us.session_start DESC
            LIMIT %s
        """, (limit,))
        
        return [{
            "user_id": row[0],
            "session_start": row[1].isoformat() if row[1] else None,
            "session_end": row[2].isoformat() if row[2] else None,
            "session_duration": str(row[3]) if row[3] else None,
            "total_interactions": row[4],
            "completed_journey": row[5],
            "health_goal": row[6],
            "medical_condition": row[7],
            "supplement_preference": row[8],
            "pueblo": row[9]
        } for row in cursor.fetchall()]
    
    @staticmethod
    def get_stage_transitions() -> List[Dict[str, Any]]:
        """Get chat flow analytics - stage transitions"""
        cursor.execute("""
            SELECT 
                stage,
                COUNT(*) as visit_count,
                AVG(EXTRACT(EPOCH FROM (created_at - LAG(created_at) OVER (PARTITION BY user_id ORDER BY created_at)))) as avg_time_in_stage
            FROM chat_state
            GROUP BY stage
            ORDER BY visit_count DESC
        """)
        
        return [{
            "stage": row[0],
            "visit_count": row[1],
            "avg_time_seconds": float(row[2]) if row[2] else 0.0
        } for row in cursor.fetchall()]
    
    @staticmethod
    def get_daily_metrics(days: int = 30) -> List[Dict[str, Any]]:
        """Get daily metrics for trend analysis"""
        cursor.execute("""
            SELECT 
                DATE(session_start) as date,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(*) as total_sessions,
                ROUND(COUNT(CASE WHEN completed_journey THEN 1 END) * 100.0 / COUNT(*), 2) as completion_rate
            FROM user_sessions
            WHERE session_start >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(session_start)
            ORDER BY date DESC
        """, (days,))
        
        return [{
            "date": row[0].isoformat(),
            "unique_users": row[1],
            "total_sessions": row[2],
            "completion_rate": float(row[3]) if row[3] else 0.0
        } for row in cursor.fetchall()]

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
            interaction_type="shown",
            stage=stage,
            user_goal=context.get("health_goal") if context else None,
            user_preference=context.get("preference") if context else None
        ) 