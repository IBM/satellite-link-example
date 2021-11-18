import json
import requests
from typing import Any
from flask_cors import CORS
import pandas as pd
import psycopg2
import os
from flask import Flask, jsonify, json, request, render_template
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

##################################################
# PostgreSQL routes
##################################################


@app.route('/')
def my_form():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    host = request.form['host']
    port = request.form['port']
    user = request.form['user']
    password = request.form['password']
    database = request.form['database']
    global conn
    global cursor
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database)
        cursor = conn.cursor()
        conn.autocommit = True
        text = "Connection Successful"
    except:
        text = "Unable to connect to database"

    return render_template('sql.html', data=text)


@app.route('/sql', methods=['POST'])
def sql():
    sql = request.form['sql']
    if "select" in sql.lower():
        try:
            cursor.execute(sql)
            text = cursor.fetchall()
            conn.commit()
        except:
            text = "Sql connection failed"
    elif "insert" in sql.lower():
        try:
            cursor.execute(sql)
            conn.commit()
            text = "Insert data successful"
        except:
            text = "Sql connection failed"
    else:
        try:
            cursor.execute(sql)
            conn.commit()
            text = "Sql statement successfully executed"
        except:
            text = "Sql connection failed"
    return render_template('sql.html', data=text)


@app.route('/logout', methods=['POST'])
def logout():
    conn.close()
    return render_template('login.html')

########################################################
# Natural Language Understanding routes
########################################################


@app.route('/login-nlu')
def my_form_nlu():
    return render_template('login-nlu.html')


@app.route('/login-nlu', methods=['POST'])
def loginNLU():
    # Add credentials to authenticate to the service instance.
    global natural_language_understanding

    try:
        serviceURL = request.form['host']
        apiKey = request.form['password']
        
        if len(serviceURL) == 0 or len(apiKey) == 0:
            text = "Provide a valid URL and API Key..."
            return render_template('login-nlu.html', data=text)

        # Create the authenticator.
        authenticator = IAMAuthenticator(apiKey)
        natural_language_understanding = NaturalLanguageUnderstandingV1(
            version='2021-03-25',
            authenticator=authenticator)

        if len(serviceURL.strip().split("://")) < 2:
            serviceURL = "https://" + serviceURL
        elif serviceURL.strip().split("://")[0].lower() != "https":
            serviceURL = "https://" + serviceURL.split("://")[1]

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
            text=text_to_analyze,
            features=Features(categories=CategoriesOptions(limit=3))).get_result()
        if response["categories"]:
            text = json.dumps(response, indent=2)

    except:
        text = f'No response from the NLU service.'

    return render_template('nlu.html', response=text, show=True)


@app.route('/logout-nlu', methods=['POST'])
def logout_nlu():
    return render_template('login-nlu.html')


port = os.getenv('VCAP_APP_PORT', '8080')
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=port)
