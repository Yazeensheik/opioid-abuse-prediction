from flask import Flask, render_template, request
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
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
    return render_template('urine.html')

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

        full_text = ""
        relevant_lines = []

        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join(word.value for word in line.words)

                    full_text += line_text + "\n"

                    if any(keyword in line_text for keyword in keywords):
                        relevant_lines.append(line_text)

        def extract_numeric(text):
            match = re.search(r'\d+', text)
            return int(match.group()) if match else None

        drug_messages = []

        for line in relevant_lines:
            numeric_value = extract_numeric(line)
            if numeric_value is not None:
                for keyword in keywords:
                    if keyword in line:
                        drug_name = keyword
                        if numeric_value > drug_toxic_levels.get(drug_name, float('inf')):
                            drug_messages.append(f"The {drug_name} level is {numeric_value} ng/mL, "
                                                 f"which is above the reference range of {drug_therapeutic_ranges.get(drug_name, 'N/A')}.")
                        else:
                            drug_messages.append(f"The {drug_name} level is {numeric_value} ng/mL, "
                                                 f"which is below or within the reference range of {drug_therapeutic_ranges.get(drug_name, 'N/A')}.")

        if drug_messages:
            if any("above" in msg for msg in drug_messages):
                prediction_message = "The patient is experiencing opioid abuse. " + " and ".join(drug_messages)
            else:
                prediction_message = "The patient is not experiencing opioid abuse. " + " ".join(drug_messages)
        else:
            prediction_message = "No relevant drug levels found."

        print("Prediction completed.")
        print(f"Prediction Message: {prediction_message}")

        return render_template('urine.html', pred=prediction_message)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return render_template('urine.html', pred="An error occurred during processing. Please try again.")

if __name__ == '__main__':
    app.run(port=3000, debug=True)
