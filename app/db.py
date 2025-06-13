import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import json
from datetime import datetime
import csv

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

def create_pueblos_table():
    """Create the pueblos table if it doesn't exist"""
    # Drop the table if it exists
    cursor.execute("DROP TABLE IF EXISTS pueblos")
    
    # Create the table with correct column names
    cursor.execute("""
        CREATE TABLE pueblos (
            "Customer Name" TEXT,
            Address TEXT,
            Pueblo TEXT
        )
    """)
    conn.commit()
    print("Table created successfully!")

def load_pharmacies_from_csv():
    """Load pharmacy data from CSV file into the database"""
    # First clear existing data
    cursor.execute("TRUNCATE TABLE pueblos")
    
    # Use direct file path
    csv_path = r"C:\Users\Felix\Desktop\Freelance_Projects\GoShopPR\Farmacias - Sheet1.csv"
    print(f"Loading data from: {csv_path}")
    
    # Read and insert CSV data
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            cursor.execute("""
                INSERT INTO pueblos ("Customer Name", Address, Pueblo)
                VALUES (%s, %s, %s)
            """, (row['Customer Name'], row['Address'], row['Pueblo']))
    
    conn.commit()
    print("Data loaded successfully!")

def get_pueblos():
    """Get all unique pueblo names from the table"""
    cursor.execute('SELECT DISTINCT Pueblo FROM pueblos ORDER BY Pueblo')
    pueblos = cursor.fetchall()
    return [row[0] for row in pueblos]

def get_pharmacy_address(user_message, limit=2):
    """
    Query the top two pharmacies from the table based on the pueblo name
    """
    cursor.execute("""
        SELECT "Customer Name", Address FROM pueblos
        WHERE Pueblo ILIKE %s
        LIMIT %s
    """, (f"%{user_message}%", limit))
    rows = cursor.fetchall()
    return [{
        "Pharmacy": row[0],
        "Location": row[1]
    } for row in rows]