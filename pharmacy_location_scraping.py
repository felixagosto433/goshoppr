# Imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import googlemaps
import time
import os
from dotenv import load_dotenv

load_dotenv(".env.google")
MAPS_API_KEY = os.getenv("MAPS_API_KEY")
SERVICE_KEY = os.getenv("SERVICE_KEY")
# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_KEY, scope)
client = gspread.authorize(creds)
sheet = client.open("Farmacias").worksheet("Sheet1")

# Google Maps API Setup
gmaps = googlemaps.Client(key=MAPS_API_KEY)

# Get pharmacy names from column A
pharmacy_names = sheet.col_values(1)[1:]  # skip header

# Loop and update column B with result
for i, name in enumerate(pharmacy_names):
    try:
        results = gmaps.places(query=name)
        if results['results']:
            place_id = results['results'][0]['place_id']
            maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
            sheet.update_cell(i+2, 2, maps_link)
        else:
            sheet.update_cell(i+2, 2, "Not found")
        time.sleep(1)
    except Exception as e:
        sheet.update_cell(i+2, 2, f"Error: {e}")
