
from typing import Any
from flask_cors import CORS
import pandas as pd
import os
from flask import Flask, jsonify, json, request, render_template
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1, Document

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)


@app.route('/')
def my_form():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    # Add credentials to authenticate to the service instance.
    global service

    try:
        serviceURL = request.form['host']
        apiKey = request.form['password']
        
        # Create the authenticator.
        authenticator = IAMAuthenticator(apiKey)
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(serviceURL)
        service_status_code = service.get_server_information(
        ).get_status_code()

        if service_status_code == 200:
            text = "Successfully connected to Cloudant"

    except:
        text = "Connection to Cloudant failed"

    return render_template('db.html', data=text)


@app.route('/db', methods=['POST'])
def createDB():
    global databaseName
    databaseName = request.form['database']
    try:
        put_database_result = service.put_database(
            db=databaseName
        ).get_result()

        if put_database_result["ok"]:
            text = f'"{databaseName}" database created.'

    except ApiException as ae:
        if ae.code == 412:
            text = f'Cannot create "{databaseName}" database, it already exists.'

    return render_template('db.html', data=text, param=True)


@app.route('/employee', methods=['POST'])
def createEmployee():
    employee_id = request.form['employeeid']
    employee_record: Document = Document(id=employee_id)

    # Add "name" and "joined" fields to the document
    employee_record.name = request.form['employeename']
    employee_record.joined = request.form['doj']
    try:
        create_document_response = service.post_document(
            db=databaseName,
            document=employee_record
        ).get_result()
        if create_document_response["rev"]:
            text = f'You have created the document:\n{employee_record}'

    except:
        text = f'Cannot create "{employee_record}" record, it already exists.'

    return render_template('db.html', data=text)


@app.route('/employees', methods=['POST'])
def getEmployees():
    try:
        read_all_employees = service.post_all_docs(
            db=databaseName,
            include_docs=True,
            startkey='abc',
            limit=2
        ).get_result()
        if read_all_employees["rows"]:
            text = f'{read_all_employees}'

    except:
        text = f'Cannot read data from the database'

    return render_template('db.html', data=text)


@app.route('/deletedb', methods=['POST'])
def deleteDatabase():
    db_to_delete = request.form['dbname']
    try:
        response = service.delete_database(db=db_to_delete).get_result()
        if response["ok"]:
            text = f'Database {db_to_delete} is now deleted!'

    except:
        text = f'Cannot find the database to delete.'

    return render_template('db.html', data=text)


port = os.getenv('VCAP_APP_PORT', '8080')
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=port)
