import os
import csv
import requests
import sys

# Read credentials from environment variables
frisbo_name = os.getenv('frisbo_name')
frisbo_pass = os.getenv('frisbo_pass')

if not frisbo_name or not frisbo_pass:
    raise ValueError("Environment variables frisbo_name and frisbo_pass must be set.")

# Obtain Bearer token
auth_url = "https://api.frisbo.ro/v1/auth/login"
auth_payload = {
    "email": frisbo_name,
    "password": frisbo_pass
}
headers = {"Content-Type": "application/json"}

response = requests.post(auth_url, json=auth_payload, headers=headers)
print("Auth response status:", response.status_code)  # Debugging
print("Auth response content:", response.text)  # Debugging

if response.status_code != 200:
    raise ValueError(f"Failed to authenticate: {response.status_code} {response.text}")

response_json = response.json()
token = response_json.get("access_token")

if not token:
    raise ValueError(f"No token received from authentication response. Response: {response_json}")

# Get organization ID from script arguments
if len(sys.argv) < 2:
    raise ValueError("Usage: python3.10 script.py <organization_id>")
organization_id = sys.argv[1]

# Define constants
API_ENDPOINT_TEMPLATE = f"https://api.frisbo.ro/v1/organizations/{organization_id}/orders/{{order_id}}/awb"
HEADERS = {"Authorization": f"Bearer {token}"}
PDF_DIR = "pdf"
CSV_FILE = "ids.csv"

# Ensure the output directory exists
os.makedirs(PDF_DIR, exist_ok=True)

def fetch_and_save_pdf(order_id):
    """Fetch the PDF for a given order ID and save it to the pdf directory."""
    try:
        url = API_ENDPOINT_TEMPLATE.format(order_id=order_id)
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            pdf_path = os.path.join(PDF_DIR, f"{order_id}.pdf")
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(response.content)
            print(f"Saved PDF for order {order_id}.")
        else:
            print(f"Failed to fetch PDF for order {order_id}. HTTP Status: {response.status_code}")
    except Exception as e:
        print(f"Error fetching PDF for order {order_id}: {e}")

# Read order IDs from the CSV file
try:
    with open(CSV_FILE, mode="r") as csv_file:
        csv_reader = csv.reader(csv_file)
        # Assuming order IDs are in the first column, skip the header if any
        next(csv_reader, None)
        for row in csv_reader:
            if row:
                order_id = row[0].strip()
                fetch_and_save_pdf(order_id)
except FileNotFoundError:
    print(f"The file {CSV_FILE} does not exist.")
except Exception as e:
    print(f"An error occurred while reading the CSV file: {e}")
