import json

import requests

# define the localhost address
API_URL = 'http://127.0.0.1:5000/predict'  
# load the example from the json file
JSON_PATH = 'api_sample.json'
# Open the JSON file
with open(JSON_PATH, 'r') as json_file:
    input_data = json.load(json_file)
# post the data
response = requests.post(API_URL, json=input_data)
# get the response
if response.status_code == 200:
    data = response.json()
    prediction = data['prediction']
    print(f"Employee whose ID is {input_data['enrollee_id']} is {'loyal' if prediction == 0.0 else 'NOT loyal'}")
else:
    print("Error:", response.status_code)
