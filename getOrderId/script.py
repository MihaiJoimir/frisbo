import pandas as pd
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

# Load the CSV file with order references
csv_file = 'order_reference.csv'
order_references = pd.read_csv(csv_file)

# API URL template
url_template = f"https://api.frisbo.ro/v1/organizations/{organization_id}/orders"
headers = {"Authorization": f"Bearer {token}"}

# List to store order_id
order_ids = []

# Iterate through each order reference and make API requests
import urllib.parse

for index, row in order_references.iterrows():
    order_reference = row['order_reference']
    
    # Construct the API URL
    encoded_order_reference = urllib.parse.quote(order_reference)
    url = f"{url_template}?order_reference={encoded_order_reference}"
    
    # Make the GET request
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the order_id if data is present
        if data['data']:
            order_id = data['data'][0]['order_id']
            order_ids.append({'order_id': order_id})
            print(f"Order ID: {order_id}")
        else:
            print(f"No data found for Order Reference: {order_reference}")
    else:
        print(f"Failed to fetch data for Order Reference: {order_reference}")
        print(f"Status Code: {response.status_code}, Response: {response.text}")

# Save the collected order_ids to an external CSV file
output_csv_file = 'order_ids.csv'
order_ids_df = pd.DataFrame(order_ids)
order_ids_df.to_csv(output_csv_file, index=False)

print(f"\nOrder IDs saved to {output_csv_file}")
