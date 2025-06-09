import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv(".env.staging")

# Database Connection
print("Connecting to Database...")
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
conn.autocommit = True
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
print("Succesfully Connected to PostgresDB")

# Functions 
def get_user_state(user_id):
    # Get the most recent state for the user using id for ordering
    cursor.execute("""
        SELECT stage, context 
        FROM chat_state 
        WHERE user_id = %s 
        ORDER BY id DESC 
        LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    if row:
        return {
            "stage": row["stage"],
            "context": row["context"]
        }
    return None

def set_user_state(user_id, state):
    # Insert new state - created_at will be set automatically by the default value
    cursor.execute("""
        INSERT INTO chat_state (user_id, stage, context)
        VALUES (%s, %s, %s)
    """, (
        user_id, 
        state["stage"], 
        json.dumps(state["context"])
    ))

def get_user_state_history(user_id, limit=50):
    """Get the state history for a user"""
    cursor.execute("""
        SELECT id, stage, context, created_at 
        FROM chat_state 
        WHERE user_id = %s 
        ORDER BY id DESC 
        LIMIT %s
    """, (user_id, limit))
    rows = cursor.fetchall()
    return [{
        "id": row["id"],
        "stage": row["stage"],
        "context": row["context"],
        "created_at": row["created_at"].isoformat()
    } for row in rows]

def reset_user_state(user_id):
    """
    Instead of deleting states, we'll just get a fresh start by 
    letting the next state be a new row
    """
    pass  # No need to delete anything since we're keeping history