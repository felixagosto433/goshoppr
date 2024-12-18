import gspread
import pandas as pd
import os
from dotenv import load_dotenv
import json

load_dotenv()

SERVICE_KEY_PATH = os.getenv("SERVICE_KEY")
print(SERVICE_KEY_PATH)
# Authenticate and connect to Google Sheets
gc = gspread.service_account(filename=SERVICE_KEY_PATH)  # Replace with your credentials file path
sheet = gc.open('Go Shop Vector Database')  # Replace with your sheet name
worksheet = sheet.worksheet('Sheet1')  # Replace with your tab name

# Fetch all records
data = worksheet.get_all_records()

# Convert to a Pandas DataFrame
df = pd.DataFrame(data)

# Define the transformation function
def transform_row(row):
    return {
        "nombre": row["nombre"], 
        "precio": row["precio"],
        "inventario": row["inventario"],
        "categoria": row["categoria"],
        "descripcion": row["descripcion"],
        "ingredientes": row["ingredientes"].split(', '),  # Split ingredients into a list
        "allergens": row["allergens"].split(', '),  # Split allergens into a list
        "usage": row["usage"],
        "recommended_for": row["recommended_for"].split(', ')  # Split recommendations into a list
    }

# Apply the transformation
json_data = [transform_row(row) for index, row in df.iterrows()]

# Save to a JSON file
with open('vitaminas.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print("Data saved to vitaminas.json!")