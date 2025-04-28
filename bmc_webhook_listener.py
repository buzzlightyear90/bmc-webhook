from flask import Flask, request, jsonify
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

# Authenticate Google Sheets API using environment variable
def get_gsheet_client():
    service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT'])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    return client

# Initialize once
gsheet_client = get_gsheet_client()
spreadsheet = gsheet_client.open("pet-portrait-orders")  # <-- Replace this
worksheet = spreadsheet.sheet1  # First sheet/tab

# Webhook route
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    data = request.json  # Parse incoming JSON data

    # Extract relevant fields
    customer_name = data.get("data", {}).get("supporter_name")
    customer_email = data.get("data", {}).get("supporter_email")
    total_amount_charged = data.get("data", {}).get("total_amount_charged")

    # Access nested commission data
    commission = data.get("data",{}).get("commission", {})
    additional_info_raw = commission.get("additional_info")
    if additional_info_raw:
        additional_info = f'"{additional_info_raw.replace(chr(34), chr(34) * 2)}"'
    else:
        additional_info = '""'

    images = commission.get("attachments", [])  # This should be a list

    # Prepare attachments as string list
    attachments_str = "[" + ", ".join(images) + "]"

    # Append new row to Google Sheet
    worksheet.append_row([
        customer_name,
        customer_email,
        additional_info,
        total_amount_charged,
        attachments_str
    ])

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run the Flask app on port 5000
