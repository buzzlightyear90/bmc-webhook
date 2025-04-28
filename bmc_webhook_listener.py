from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_service_account.json', scope)
client = gspread.authorize(creds)
sheet = client.open("pet-portrait-orders").sheet1

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

    # Insert a new row in the Google Sheet
    new_row = [customer_name, customer_email, additional_info, total_amount_charged, attachments_str]
    sheet.append_row(new_row, value_input_option="USER_ENTERED")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run the Flask app on port 5000
