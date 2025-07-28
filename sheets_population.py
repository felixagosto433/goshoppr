import psycopg2
import psycopg2.extras
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

load_dotenv(".env.google")

# Database connection
print("Connecting to Database...")
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
print("CONNECTED!")

# Google Sheets connection
print("Connecting to Google Sheets...")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SERVICE_KEY = os.getenv("SERVICE_KEY")
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_KEY, scope)
client = gspread.authorize(creds)
print("CONNECTED!")

def export_table_to_sheet(cursor, sheet_name, query):
    print(f"Exporting to {sheet_name}")
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)

    # ✅ Convert all datetime columns to strings
    for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]', 'object']):
        df[col] = df[col].astype(str)

    sheet = client.open("GoShop_Database").worksheet(sheet_name)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print(f"Export Completed!")

# Export each table
export_table_to_sheet(cur, "chat_state", "SELECT * FROM chat_state")
export_table_to_sheet(cur, "location_analytics", "SELECT * FROM location_analytics")
export_table_to_sheet(cur, "product_interactions", "SELECT * FROM product_interactions")
export_table_to_sheet(cur, "user_goals", "SELECT * FROM user_goals")
export_table_to_sheet(cur, "user_sessions", "SELECT * FROM user_sessions")

conn.close()
