import pickle
import os
import pandas as pd
import joblib
# Define the directory where the models and preprocessing objects are saved
save_directory = r"E:\CTS\opioid Abuse Prediction\model"


# Load preprocessing objects
with open(os.path.join(save_directory, 'self_analysis_preprocessing_objects.pkl'), 'rb') as f:
    preprocessing_objects = pickle.load(f)

# Extract the encoders, imputer, and scaler
encoders = preprocessing_objects['encoders']
knn_imputer = preprocessing_objects['knn_imputer']
scaler = preprocessing_objects['scaler']

# Load the ensemble model
with open(os.path.join(save_directory, 'self_analysis_ensemble_model.pkl'), 'rb') as f:
    ensemble_model = pickle.load(f)

# New patient data
new_patient = pd.DataFrame({
    'Age': [45],
    'Gender': ['Male'],
    'Family History of Substance Abuse': ['No'],
    'Personal History of Substance Abuse': ['Yes'],
    'History of Mental Health Conditions': ['Yes'],
    'Chronic Pain Conditions': ['Yes'],
    'Prescribed Medications': ['Oxycodone'],
    'Dosage': ['10mg'],
    'Frequency': ['2 times per day'],
    'Duration of Opioid Medication Use': ['1 year'],
    'History of Overdose or Hospitalization Due to Opioid Use': ['No'],
    'Social Support Network': ['Strong support system']
})

# Encode new patient data using the loaded encoders
new_patient_encoded = pd.DataFrame(columns=new_patient.columns)
for feature in encoders.keys():
    le = encoders[feature]
    new_patient_encoded[feature] = le.transform(new_patient[feature])

# Keep the age column as is (no encoding needed)
new_patient_encoded['Age'] = new_patient['Age']

# Impute missing values using the loaded KNN imputer
new_patient_imputed = knn_imputer.transform(new_patient_encoded)

# Scale the data using the loaded StandardScaler
new_patient_scaled = scaler.transform(new_patient_imputed)
# Predict the risk level using the loaded ensemble model
predicted_class = ensemble_model.predict(new_patient_scaled)

# Define risk levels mapping
risk_levels = {
    0: "Very Low Risk",
    1: "Low Risk",
    2: "Medium Risk",
    3: "High Risk",
    4: "Very High Risk"
}

# Output the predicted risk level
print("Predicted Opioid Risk Level:", risk_levels[predicted_class[0]])
