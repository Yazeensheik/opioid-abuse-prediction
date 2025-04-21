from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from datetime import datetime, timedelta
import re
keywords = ['Codeine', 'Demerol', 'Fentanyl', 'Hydrocodone', 'Kadian', 'Methadone',
            'Morphine', 'Opana', 'Oxycodone', 'Tramadol', 'Vicodin']

# Load the pre-trained OCR model
model = ocr_predictor(pretrained=True)

# Load the image as a document
doc = DocumentFile.from_images(r"E:\CTS\opioid Abuse Prediction\data\prescription.jpg")

# Perform OCR on the document
result = model(doc)

# Initialize a variable to store the accumulated text
extracted_text = ""

# Process the OCR results
for page in result.pages:
    for block in page.blocks:
        for line in block.lines:
            # Join words with a space and add line breaks at the end of each line
            line_text = " ".join(word.value for word in line.words)
            extracted_text += line_text + "\n"
        # Add a line break between blocks
        extracted_text += "\n"

# Print the accumulated text
print("Extracted Text:")
print(extracted_text)
def notify_patient_if_keywords_found(corrected_text, keywords,date):
    for keyword in keywords:
        if keyword.upper() in corrected_text.upper():
            print(f"Notify the patient for consultation on {date}.")
            break
def extract_date_from_text(corrected_text):
    # Regular expression to find dates in formats like DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, etc.
    date_pattern = r'\b(\d{1,2}[-/\s]\d{1,2}[-/\s]\d{2,4}|\d{4}[-/\s]\d{1,2}[-/\s]\d{1,2})\b'
    match = re.search(date_pattern, corrected_text)

    if match:
        date_str = match.group(0)
        try:
            # Attempt to parse the extracted date
            date_formats = ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj
                except ValueError:
                    continue
        except ValueError:
            return None
    return None


# Function to calculate the date after 2 months and format it as dd/mm/yyyy
def calculate_date_after_2_months(original_date):
    # Add two months to the original date
    new_date = original_date + timedelta(days=60)  # Approximation, can be adjusted for exact months
    return new_date.strftime("%d/%m/%Y")  # Format the new date as dd/mm/yyyy


extracted_date = extract_date_from_text(extracted_text)
if extracted_date:
    date_after_2_months = calculate_date_after_2_months(extracted_date)

else:
    print("No valid date found in the corrected text.")
notify_patient_if_keywords_found(extracted_text, keywords, date_after_2_months)