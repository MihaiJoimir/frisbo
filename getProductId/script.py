import csv
import requests
import os

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

# Read the SKU from the input CSV file
input_csv_path = 'sku.csv'
sku_list = []
with open(input_csv_path, mode='r', newline='', encoding='utf-8') as input_file:
    csv_reader = csv.reader(input_file)
    next(csv_reader, None)  # Skip the header if present
    for row in csv_reader:
        if row:  # Avoid empty rows
            sku_list.append(row[0])

print("SKUs to fetch:", sku_list)  # Debugging

# Get organization ID from script arguments
import sys
if len(sys.argv) < 2:
    raise ValueError("Usage: python3.10 script.py <organization_id>")
organization_id = sys.argv[1]

# API details
api_url_template = f'https://api.frisbo.ro/v1/organizations/{organization_id}/products?sku_contains={{}}'
headers = {
    'Authorization': f'Bearer {token}',
}

# Output CSV with both SKU and product_id
output_csv_path = 'product_ids.csv'

with open(output_csv_path, mode='w', newline='', encoding='utf-8') as output_file:
    csv_writer = csv.writer(output_file)
    csv_writer.writerow(['sku', 'product_id'])  # Write header with both columns

    for sku in sku_list:
        response = requests.get(api_url_template.format(sku), headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):  # Check if there's data in the response
                product_id = data['data'][0].get('product_id')
                print(f"SKU: {sku}, Product ID: {product_id}")  # Debugging
                csv_writer.writerow([sku, product_id])  # Write SKU and product_id
            else:
                print(f"No product found for SKU: {sku}")
        else:
            print(f"Failed to get product info for SKU: {sku}. Status code: {response.status_code}")

print(f"\nSKU and Product IDs have been saved to {output_csv_path}")
