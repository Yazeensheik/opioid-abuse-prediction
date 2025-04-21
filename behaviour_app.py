import pickle
import os
import pandas as pd
import numpy as np
from flask import Flask, request, render_template

app = Flask(__name__)

save_directory = r"E:\CTS\opioid Abuse Prediction\model"

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

@app.route('/')
def hello_world():
    return render_template("behaviour.html")  # Your template name can be different; adjust accordingly

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        # Get input data from the form
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

        return render_template('behaviour.html', pred=f'Predicted Opioid Risk Level: {predicted_risk_level}')
    else:
        return render_template('behaviour.html')

if __name__ == '__main__':
    app.run(debug=True)
