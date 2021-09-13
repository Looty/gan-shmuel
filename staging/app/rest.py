import pymysql
from app import app
from db import mysql
from flask import jsonify

@app.route('/')
def users():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id FROM containers")
    rows = cursor.fetchall()
    resp = jsonify(rows)
    resp.status_code = 200
    return resp


@app.route("/health", methods=['GET'])
def health():
    return 'ok'

@app.route("/unknown", methods=['GET'])
def unknown():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT distinct id FROM containers WHERE weight IS NULL")
    rows = cursor.fetchall()
    resp = jsonify(rows)
    resp.status_code = 200
    return resp





if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
