import os
import pickle
import pandas as pd
import numpy as np
import cv2
import re
from flask import Flask, request, render_template,send_file
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from datetime import datetime, timedelta
from google.generativeai import configure, GenerativeModel
import io
from fpdf import FPDF
from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['opioid']
collection = db['report_details']
collection1 = db['patient_details']

# Load Models and Preprocessing Objects
save_directory = r"E:\opioid Abuse Prediction\opioid Abuse Prediction\model"
with open(os.path.join(save_directory, 'self_analysis_preprocessing_objects.pkl'), 'rb') as f:
    preprocessing_objects_self_analysis = pickle.load(f)

encoders_self_analysis = preprocessing_objects_self_analysis['encoders']
knn_imputer_self_analysis = preprocessing_objects_self_analysis['knn_imputer']
scaler_self_analysis = preprocessing_objects_self_analysis['scaler']

with open(os.path.join(save_directory, 'self_analysis_ensemble_model.pkl'), 'rb') as f:
    ensemble_model_self_analysis = pickle.load(f)

risk_levels_self = {
    0: "Low Risk",
    1: "Low Risk",
    2: "Medium Risk",
    3: "High Risk",
    4: "High Risk"
}

with open(os.path.join(save_directory, 'behaviour_preprocessing_objects.pkl'), 'rb') as f:
    preprocessing_objects = pickle.load(f)

encoders = preprocessing_objects['encoders']
knn_imputer = preprocessing_objects['knn_imputer']
scaler = preprocessing_objects['scaler']

with open(os.path.join(save_directory, 'behaviour_ensemble_model.pkl'), 'rb') as f:
    ensemble_model = pickle.load(f)

risk_levels = {
    0: "Low Risk",
    1: "Medium Risk",
    2: "High Risk",
    3: "High Risk"
}

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
def calculate_pupil_size(image_path, pixel_to_mm_conversion_factor):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print("Error: Unable to load the image. Please check the file path.")
        return None

    blurred_image = cv2.GaussianBlur(image, (7, 7), 0)

    circles = cv2.HoughCircles(blurred_image, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
                               param1=50, param2=30, minRadius=10, maxRadius=50)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        for (x, y, r) in circles:
            pupil_size_mm = r * pixel_to_mm_conversion_factor

            cv2.circle(image, (x, y), r, (255, 255, 255), 2)
            cv2.circle(image, (x, y), 2, (255, 255, 255), 3)

            print(f"Pupil size: {pupil_size_mm:.2f} mm")

            if pupil_size_mm < 2.5:
                print("Warning: The person may be abusing opioids (pupil size < 2.5 mm).")

            return pupil_size_mm
    else:
        print("Pupil not detected.")
        return None


@app.route('/', methods=['GET', 'POST'])
def createID():
    if request.method == 'POST':
        try:
            input_data = {
                'Patient Name': request.form['Name'],
                'Date of Birth': datetime.strptime(request.form['Date_of_Birth'], '%Y-%m-%d'),  # Ensure proper format
                'Gender': request.form['Gender'],
                'Contact Number': request.form['Contact_Number'],
                'Email ID': request.form['Email_ID'],
                'Address': request.form['Address']
            }

            collection1.insert_one({
                "route": "createID",
                "timestamp": datetime.utcnow(),
                "data": input_data
            })
            return render_template('createID.html', message="Patient data stored successfully!")
        except Exception as e:
            return render_template('createID.html', message=f"Error occurred: {str(e)}")
    return render_template('createID.html')

@app.route('/behaviour', methods=['GET', 'POST'])
def behaviour():
    if request.method == 'POST':
        input_data = {
            'Sex': [request.form['Sex']],
            'Age': [int(request.form['Age'])],
            'History of preadolescent sexual abuse': [request.form['History of preadolescent sexual abuse']],
            'History of depression': [request.form['History of depression']],
            'History of ADD, OCD, bipolar disorder, or schizophrenia': [request.form['History of ADD, OCD, bipolar disorder, or schizophrenia']],
            'Personal history of alcohol abuse': [request.form['Personal history of alcohol abuse']],
            'Personal history of illegal drug abuse': [request.form['Personal history of illegal drug abuse']],
            'Personal history of prescription drug abuse': [request.form['Personal history of prescription drug abuse']],
            'Family history of alcohol abuse': [request.form['Family history of alcohol abuse']],
            'Family history of illegal drug abuse': [request.form['Family history of illegal drug abuse']],
            'Family history of prescription drug abuse': [request.form['Family history of prescription drug abuse']]
        }

        new_patient = pd.DataFrame(input_data)

        new_patient_encoded = pd.DataFrame(columns=new_patient.columns)
        for feature in encoders.keys():
            le = encoders[feature]
            new_patient_encoded[feature] = le.transform(new_patient[feature])

        new_patient_encoded['Age'] = new_patient['Age']

        new_patient_imputed = knn_imputer.transform(new_patient_encoded)
        new_patient_scaled = scaler.transform(new_patient_imputed)

        predicted_class = ensemble_model.predict(new_patient_scaled)
        predicted_risk_level = risk_levels[predicted_class[0]]

        collection.insert_one({
            "route": "behaviour",
            "timestamp": datetime.utcnow(),
            "data": {
                "Behaviour Analysis": predicted_risk_level
            }
        })

        return render_template('behaviour.html', pred=f'Predicted Opioid Risk Level: {predicted_risk_level}')
    else:
        return render_template('behaviour.html')

@app.route('/blood', methods=['GET', 'POST'])
def blood():
    if request.method == 'POST':
        try:
            imagefile = request.files['imagefile']
            image_path = os.path.join("./images", imagefile.filename)
            imagefile.save(image_path)
            print("image saved")
            model = ocr_predictor(pretrained=True)
            print("ocr model loaded")
            doc = DocumentFile.from_images(image_path)
            result = model(doc)

            relevant_lines = []
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        line_text = " ".join(word.value for word in line.words)
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

            drug_messages_str = "\n".join(drug_messages)

            print(drug_messages_str)
            print(type(drug_messages_str))
            print(type(drug_messages))
            collection.insert_one({
                "route": "blood",
                "timestamp": datetime.utcnow(),
                "data": {
                    "Blood Test Drug Name" : drug_name,
                    "Blood Test Drug Value" : numeric_value
                }
            })

            return render_template('blood.html', bpred=prediction_message)
        except Exception as e:
            return render_template('blood.html', bpred="An error occurred during processing. Please try again.")
    else:
        return render_template('blood.html')

@app.route('/urine', methods=['GET', 'POST'])
def urine():
    if request.method == 'POST':
        try:
            imagefile = request.files['imagefile']
            image_path = os.path.join("./images", imagefile.filename)
            imagefile.save(image_path)
            print("image saved")
            model = ocr_predictor(pretrained=True)
            print("ocr model loaded")
            doc = DocumentFile.from_images(image_path)
            result = model(doc)

            relevant_lines = []
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        line_text = " ".join(word.value for word in line.words)
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

            drug_messages_str = "\n".join(drug_messages)

            print(drug_messages_str)
            print(type(drug_messages_str))
            print(type(drug_messages))

            collection.insert_one({
                "route": "urine",
                "timestamp": datetime.utcnow(),
                "data": {
                    "Urine Test Drug Name" : drug_name,
                    "Urine Test Drug Value" : numeric_value
                }
            })

            return render_template('urine.html', upred=prediction_message)
        except Exception as e:
            return render_template('urine.html', upred="An error occurred during processing. Please try again.")
    else:
        return render_template('urine.html')

@app.route('/pupil', methods=['GET', 'POST'])
def pupil():
    if request.method == 'POST':
        try:
            imagefile = request.files['imagefile']
            image_path = os.path.join("./images", imagefile.filename)
            imagefile.save(image_path)

            print(f"Image saved at: {image_path}")

            pixel_to_mm_conversion_factor = 0.1

            pupil_size_mm = calculate_pupil_size(image_path, pixel_to_mm_conversion_factor)

            if pupil_size_mm is not None:
                prediction_message = f"Pupil size: {pupil_size_mm:.2f} mm"
                if pupil_size_mm < 2.5:
                    prediction_message += " - Warning: The person may be abusing opioids (pupil size < 2.5 mm)."
            else:
                prediction_message = "Pupil not detected."

            collection.insert_one({
                "route": "pupil",
                "timestamp": datetime.utcnow(),
                "data": {
                    "Pupil Size": pupil_size_mm
                }
            })

            return render_template('pupil.html', pred=prediction_message)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return render_template('pupil.html', pred="An error occurred during processing. Please try again.")
    else:
        return render_template('pupil.html')

@app.route('/final',methods=['GET','post'])
def final():
    return render_template('report.html')

if __name__ == '__main__':
    app.run(debug=True)