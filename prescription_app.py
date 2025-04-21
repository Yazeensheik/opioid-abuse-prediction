from flask import Flask, render_template, request
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from datetime import datetime, timedelta
import re
import os

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

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('prescription.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        imagefile = request.files['imagefile']
        image_path = os.path.join("./images", imagefile.filename)
        imagefile.save(image_path)

        print(f"Image saved at: {image_path}")

        model = ocr_predictor(pretrained=True)

        doc = DocumentFile.from_images(image_path)
        print("Image loaded for OCR processing.")

        result = model(doc)
        print("OCR processing completed.")

        extracted_text = ""

        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join(word.value for word in line.words)
                    extracted_text += line_text + "\n"
                extracted_text += "\n"

        print("Extracted Text:")
        print(extracted_text)

        def extract_numeric(text):
            match = re.search(r'\d+', text)
            return int(match.group()) if match else None

        def extract_date_from_text(text):
            date_pattern = r'\b(\d{1,2}[-/\s]\d{1,2}[-/\s]\d{2,4}|\d{4}[-/\s]\d{1,2}[-/\s]\d{1,2})\b'
            match = re.search(date_pattern, text)
            if match:
                date_str = match.group(0)
                try:
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

        def calculate_date_after_2_months(original_date):
            new_date = original_date + timedelta(days=60)  
            return new_date.strftime("%d/%m/%Y")

        def notify_patient_if_keywords_found(text, keywords, date):
            notifications = []
            for keyword in keywords:
                if keyword.upper() in text.upper():
                    notifications.append(f"Notify the patient for consultation on {date}.")
            return notifications

        extracted_date = extract_date_from_text(extracted_text)
        if extracted_date:
            date_after_2_months = calculate_date_after_2_months(extracted_date)
        else:
            date_after_2_months = "N/A"

        notifications = notify_patient_if_keywords_found(extracted_text, keywords, date_after_2_months)
        prediction_message = " ".join(notifications) if notifications else "No relevant keywords found."

        print("Prediction completed.")
        print(f"Prediction Message: {prediction_message}")

        return render_template('prescription.html', pred=prediction_message)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return render_template('prescription.html', pred="An error occurred during processing. Please try again.")

if __name__ == '__main__':
    app.run(port=3000, debug=True)
