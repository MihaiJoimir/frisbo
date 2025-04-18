import re
import csv
import os
import pdfplumber

# Function to extract names and AWB codes from a page
def extract_name_and_awb(page_text):
    data = []
    awb_pattern = r"AWB:\s*(\d+)"
    contact_pattern = r"Contact:\s*([A-Za-z\-\s\.]+)"  # Pattern to capture names

    awb_matches = re.findall(awb_pattern, page_text)
    contact_matches = re.findall(contact_pattern, page_text)

    # Process names without truncations
    names = []
    for name in contact_matches:
        names.append(name.strip())

    # Log extracted names for debugging
    print("Extracted Names:", names)

    # Pair names and AWB codes
    for name, awb in zip(names, awb_matches):
        data.append({"Name": name.strip(), "AWB": awb.strip()})
    return data

# Directory containing the PDF files
pdf_directory = os.getcwd()
output_csv_path = "awb_data.csv"

# Initialize an empty list to hold all extracted data
all_extracted_data = []

# Loop through all files in the directory
for file_name in os.listdir(pdf_directory):
    if file_name.endswith(".pdf"):
        file_path = os.path.join(pdf_directory, file_name)
        print(f"Processing {file_name}...")

        # Use pdfplumber to extract text
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if not page_text:
                    print(f"Warning: No text extracted from {file_name}. Check PDF formatting.")
                    continue
                all_extracted_data.extend(extract_name_and_awb(page_text))

# Write all data to a single CSV file
with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ["Name", "AWB"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(all_extracted_data)

print(f"Data successfully extracted and saved to {output_csv_path}.")
