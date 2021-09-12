import pymysql
from app import app
from db import mysql
from flask import jsonify
import requests

@app.route('/')
@app.route('/index')
def index():
    return "tryagen"
@app.route('/health', methods=['GET'])
def helth():
    services = {"unknown"}
    for service in services:
        req = requests.get(f"http://localhost:5000/{service}")
        status_code = req.status_code
        if status_code < 200 or status_code > 299:
            result = f"service {service} : {status_code} server error"
            return result
        else:
            result = ""
            for service in services:
                result += f"Service {service} ... ok"
            return result

    

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')

