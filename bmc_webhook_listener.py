from flask import Flask, request, jsonify
import json
import csv
import os

app = Flask(__name__)

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

    # CSV file path
    csv_filename = "orders.csv"
    file_exists = os.path.isfile(csv_filename)

    # Append to CSV
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writerow(["name", "email", "additional info", "total amount charged", "attachments"])

        writer.writerow([
            customer_name,
            customer_email,
            additional_info,
            total_amount_charged,
            attachments_str
        ])


    # # Save the extracted data
    # order_details = f"""
    # Name: {customer_name}
    # Email: {customer_email}
    # Additional Info: {additional_info}
    # Total Amount Charged: {total_amount_charged}
    # Attachments: {images}
    # """

    # print(order_details)

    # # Save details to a file (optional)
    # with open("bmc_orders.txt", "a") as file:
    #     file.write(order_details + "\n")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Run the Flask app on port 5000
