import json
import requests
from flask_cors import CORS
import pandas as pd
import psycopg2
import os
from flask import Flask, jsonify, json, request, render_template


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)


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
    port= port,
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
    		text = cursor.fetchall();
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
    		text  = "Sql connection failed"
    return render_template('sql.html', data=text)

@app.route('/logout', methods=['POST'])
def logout():
	conn.close()
	return render_template('login.html')



port = os.getenv('VCAP_APP_PORT', '8080')
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=port)