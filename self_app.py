import pickle
import os
import pandas as pd
import numpy as np
from flask import Flask, request, render_template

app = Flask(__name__)

save_directory = r"E:\CTS\opioid Abuse Prediction\model"

with open(os.path.join(save_directory, 'self_analysis_preprocessing_objects.pkl'), 'rb') as f:
    preprocessing_objects = pickle.load(f)

encoders = preprocessing_objects['encoders']
knn_imputer = preprocessing_objects['knn_imputer']
scaler = preprocessing_objects['scaler']

with open(os.path.join(save_directory, 'self_analysis_ensemble_model.pkl'), 'rb') as f:
    ensemble_model = pickle.load(f)

risk_levels = {
    0: "Low Risk",
    1: "Low Risk",
    2: "Medium Risk",
    3: "High Risk",
    4: "High Risk"
}

@app.route('/')
def hello_world():
    return render_template("self_analysis.html")  

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        input_data = {
           'Age': [int(request.form['Age'])],
           'Gender': [request.form['Gender']],
            'Family History of Substance Abuse': [request.form['Family History of Substance Abuse']],
            'Personal History of Substance Abuse': [request.form['Personal History of Substance Abuse']],
            'History of Mental Health Conditions': [request.form['History of Mental Health Conditions']],
            'Chronic Pain Conditions': [request.form['Chronic Pain Conditions']],
            'Prescribed Medications': [request.form['Prescribed Medications']],
            'Dosage': [request.form['Dosage']],
            'Frequency': [request.form['Frequency']],
            'Duration of Opioid Medication Use': [request.form['Duration of Opioid Medication Use']],
            'History of Overdose or Hospitalization Due to Opioid Use': [request.form['History of Overdose or Hospitalization Due to Opioid Use']],
            'Social Support Network': [request.form['Social Support Network']]
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

        return render_template('self_analysis.html', pred=f'Predicted Opioid Risk Level: {predicted_risk_level}')
    else:
        return render_template('self_analysis.html')

if __name__ == '__main__':
    app.run(debug=True)
