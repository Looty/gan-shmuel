import pymysql
from app import app
from db import mysql
from flask import jsonify
@app.route('/')
@app.route('/index')
def index():
    return "H7A"
@app.route('/health', methods=['GET'])
def helth():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT 1")
    rows = cursor.fetchall()
    resp = jsonify(rows)
    resp.status_code = 200
    return resp
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
