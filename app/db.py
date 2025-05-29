import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import json

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
    cursor.execute("SELECT stage, context FROM chat_state WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    if row:
        return {
            "stage": row["stage"],
            "context": row["context"]
        }
    return None

def get_user_context(user_id):
    cursor.execute("SELECT context FROM chat_state WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    if row:
        return row["context"]
    return {}

def set_user_state(user_id, state):
    cursor.execute("""
        INSERT INTO chat_state (user_id, stage, context)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET stage = EXCLUDED.stage, context = EXCLUDED.context
    """, (user_id, state["stage"], json.dumps(state["context"])))

def set_user_context(user_id, context):
    cursor.execute("""
        UPDATE chat_state
        SET context = %s
        WHERE user_id = %s
    """, (json.dumps(context), user_id))

def reset_user_state(user_id):
    cursor.execute("DELETE FROM chat_state WHERE user_id = %s", (user_id,))