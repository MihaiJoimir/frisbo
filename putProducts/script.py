import csv
import requests
import os
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

# API details
API_URL_TEMPLATE = f"https://api.frisbo.ro/v1/organizations/{organization_id}/products?product_id={{product_id}}"
HEADERS = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# File path
CSV_FILE_PATH = "input.csv"

def send_product_data(product):
    """Send product data to the Frisbo API."""
    url = API_URL_TEMPLATE.format(product_id=product["id"])
    response = requests.put(url, json=product, headers=HEADERS)
    return response.status_code, response.text

# Read CSV and send data
with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        product_data = {
            "id": row["product_id"],
            "name": row["name"],
            "sku": row["sku"],
            "upc": row.get("upc", ""),
            "external_code": row.get("external_code", ""),
            "ean": row.get("ean", ""),
            "vat": float(row.get("vat", 0)),
            "dimensions": {
                "width": float(row.get("dimensions.width", 0)),
                "height": float(row.get("dimensions.height", 0)),
                "length": float(row.get("dimensions.length", 0)),
                "weight": float(row.get("dimensions.weight", 0))
            },
            "has_lot": 1
        }
        
        status, response_text = send_product_data(product_data)
        print(f"Product ID {product_data['id']}: Status {status}")
