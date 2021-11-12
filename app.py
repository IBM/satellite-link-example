
from typing import Any
from flask_cors import CORS
import pandas as pd
import os
from flask import Flask, jsonify, json, request, render_template
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)


@app.route('/')
def my_form():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    # Add credentials to authenticate to the service instance.
    global natural_language_understanding

    try:
        serviceURL = request.form['host']
        apiKey = request.form['password']
        
        # Create the authenticator.
        authenticator = IAMAuthenticator(apiKey)
        natural_language_understanding = NaturalLanguageUnderstandingV1(
            version='2021-03-25',
            authenticator=authenticator)
            
        natural_language_understanding.set_service_url(serviceURL)

        service_status_code = natural_language_understanding.list_models().get_status_code()

        if service_status_code == 200:
            text = "Successfully connected to NLU service"

    except:
        text = "Connection to NLU service failed"

    return render_template('nlu.html', data=text)


@app.route('/nlu', methods=['POST'])
def connect():
    global databaseName
    text_to_analyze = request.form['nlu']
    
    try:
        response = natural_language_understanding.analyze(
            text= text_to_analyze,
            features=Features(categories=CategoriesOptions(limit=3))).get_result()
        if response["categories"]:
            text = json.dumps(response, indent=2)

    except:
        text = f'No response from the NLU service.'

    return render_template('nlu.html', response=text, show = True)


port = os.getenv('VCAP_APP_PORT', '8080')
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=port)
