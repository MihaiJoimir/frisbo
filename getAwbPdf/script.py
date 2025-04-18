import re
from PyPDF2 import PdfReader, PdfWriter

# Define the input and output file paths
input_file = "AWB.pdf"  # Path to your input PDF
output_folder = "output/"  # Folder to save the extracted PDFs

# Regular expression to find the AWB number
awb_pattern = re.compile(r'(\d{13})')

# Read the PDF file
reader = PdfReader(input_file)

for i, page in enumerate(reader.pages):
    text = page.extract_text()
    match = awb_pattern.search(text)
    if match:
        awb_number = match.group(1)
        output_file = f"{output_folder}/{awb_number}.pdf"

        # Write the page to a new PDF
        writer = PdfWriter()
        writer.add_page(page)
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        print(f"Saved page {i + 1} with AWB {awb_number} to {output_file}")

