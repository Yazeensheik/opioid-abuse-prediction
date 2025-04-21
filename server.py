from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from pymongo import MongoClient


app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://<visakangamer>:<vptBLAOFCJNMVuKc>@cluster0.mongodb.net/<opioid>?retryWrites=true&w=majority"
mongo = PyMongo(app)



@app.route('/')
def index():
    return render_template('behaviour.html')

@app.route('/behaviour', methods=['POST'])
def behaviour():
    # Retrieve form data
    sex = request.form.get('Sex')
    age = request.form.get('Age')
    preadolescent_abuse = request.form.get('History of preadolescent sexual abuse')
    depression = request.form.get('History of depression')
    mental_health = request.form.get('History of ADD, OCD, bipolar disorder, or schizophrenia')
    alcohol_abuse = request.form.get('Personal history of alcohol abuse')
    illegal_drug_abuse = request.form.get('Personal history of illegal drug abuse')
    prescription_drug_abuse = request.form.get('Personal history of prescription drug abuse')
    family_alcohol_abuse = request.form.get('Family history of alcohol abuse')
    family_illegal_drug_abuse = request.form.get('Family history of illegal drug abuse')
    family_prescription_drug_abuse = request.form.get('Family history of prescription drug abuse')

    # Prepare data to be inserted into MongoDB
    data = {
        'sex': sex,
        'age': age,
        'preadolescent_abuse': preadolescent_abuse,
        'depression': depression,
        'mental_health': mental_health,
        'alcohol_abuse': alcohol_abuse,
        'illegal_drug_abuse': illegal_drug_abuse,
        'prescription_drug_abuse': prescription_drug_abuse,
        'family_alcohol_abuse': family_alcohol_abuse,
        'family_illegal_drug_abuse': family_illegal_drug_abuse,
        'family_prescription_drug_abuse': family_prescription_drug_abuse
    }

    # Insert data into MongoDB
    mongo.db.behaviour_analysis.insert_one(data)

    # Redirect to a success page or render a template
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
