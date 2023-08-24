import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from joblib import load

app = Flask(__name__)

# THIS ASSUMES TO HAVE A FRONT END, WHERE THE USERS CAN SPECIFY ALL THE FEATURES 
# AVAILABLE ORIGINALLY IN THE .csv. THE PREPROCESSING IS DONE ACCORDINGLY.
# As input we then have an instance with 13 features:
#  0   enrollee_id             
#  1   city -> 0 to 180                 
#  2   city_development_index -> 0.0 to 1.0
#  3   gender -> Male, Female, Others, not_specified                
#  4   relevent_experience -> Has relevent experience,  No relevent experience
# ... as done in exploratory analysis

# Of Course to limit the network traffic we can eventually decide to send
# only the 4 relevant features

# Load the trained classifier
clf = load('clf.joblib')

def preprocess_input(input_data):
    """
    Preprocess the input data and extract relevant features for prediction.
    """
    
    # the input data is a json, we want a series
    data = pd.Series(input_data)
    # the features of interest are only 4: 
    # ['city_development_index', 'experience', 'city_21', 'company_type_not_specified']
    
    # transform city to boolean city_21
    data['city_21'] = 0.0 if data['city'] != 21 else 1.0
    # tranform company_type
    data['company_type_not_specified'] = 1.0 if data['company_type'] == 'not_specified' else 0.0
    # convert experience to int
    # define an ad-hoc function
    def convert_experience_to_int(row):
        if row is np.nan:
            return '-1'
        elif row == '<1':
            return '0'
        elif row == '>20':
            return '21'
        else:
            return int(row)

    # Apply it!
    data['experience'] = convert_experience_to_int(data['experience'])

    # select only the relevant features to feed the model
    preprocessed_data = data[['city_development_index', 'experience', 'city_21', 'company_type_not_specified']]

    return preprocessed_data

# def load_the model and to the prediction
def make_prediction(input_data):
    return clf.predict(input_data.to_numpy().reshape(1, -1))


@app.route('/predict', methods=['POST'])
def predict_employee_churn():
    data = request.json  # Get data from JSON input
    
    # Preprocess input data
    input_data = preprocess_input(data)
    
    # Make predictions
    predictions = make_prediction(input_data)
    
    return jsonify({'prediction': predictions.tolist()[0]})

if __name__ == '__main__':
    app.run(debug=True)
   
    
    
