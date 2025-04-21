from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import re

# Dictionaries for therapeutic ranges and toxic levels
drug_therapeutic_ranges = {
    "Morphine": "10–80 ng/mL",
    "Codeine": "150–300 ng/mL",
    "Oxycodone": "10–100 ng/mL",
    "Hydrocodone": "10–50 ng/mL",
    "Fentanyl": "1–3 ng/mL",
    "Methadone": "300–1000 ng/mL",
    "Buprenorphine": "0.5–2 ng/mL",
    "Hydromorphone": "10–50 ng/mL",
    "Tramadol": "100–300 ng/mL"
}
drug_toxic_levels = {
    "Morphine": 200,
    "Codeine": 2000,
    "Oxycodone": 200,
    "Hydrocodone": 100,
    "Fentanyl": 10,
    "Methadone": 2000,
    "Buprenorphine": 10,
    "Hydromorphone": 80,
    "Tramadol": 600
}
keywords = ['Morphine', 'Codeine', 'Oxycodone', 'Hydrocodone', 'Fentanyl', 'Methadone',
            'Buprenorphine', 'Hydromorphone', 'Tramadol']

# Initialize the OCR model
model = ocr_predictor(pretrained=True)

# Load the image as a document
doc = DocumentFile.from_images(r"E:\CTS\opioid Abuse Prediction\data\blood report.jpg")

# Perform OCR on the document
result = model(doc)

# Initialize variables to store the full text and relevant lines
full_text = ""
relevant_lines = []

# Process each page in the document
for page in result.pages:
    for block in page.blocks:
        for line in block.lines:
            # Join words with a space
            line_text = " ".join(word.value for word in line.words)

            # Append the full text
            full_text += line_text + "\n"

            # Check if any keyword is in the line
            if any(keyword in line_text for keyword in keywords):
                relevant_lines.append(line_text)

# Define a function to check if a line contains numeric value
def extract_numeric(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None

# Process the relevant lines
print("Full Extracted Text:")
print(full_text)
print("\n" + "=" * 50 + "\n")  # Separator

print("Relevant Lines:")
for line in relevant_lines:
    numeric_value = extract_numeric(line)
    if numeric_value is not None:
        # Extract drug name from the line (assume it appears at the start of the line)
        for keyword in keywords:
            if keyword in line:
                drug_name = keyword
                if numeric_value > drug_toxic_levels.get(drug_name, float('inf')):
                    # Print drug name, level, and therapeutic range
                    print(f"The patient is experiencing opioid abuse. The {drug_name} level is {numeric_value} ng/mL, which is above the reference range of  {drug_therapeutic_ranges.get(drug_name, 'N/A')} ")
                else:
                    print(f"The patient is not experiencing opioid abuse. The {drug_name} level is {numeric_value} ng/mL, which is below or within the reference range of {drug_therapeutic_ranges.get(drug_name, 'N/A')}.")

