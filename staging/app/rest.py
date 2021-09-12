import pymysql
from app import app
from db import mysql
from flask import jsonify
@app.route('/')
@app.route('/index')
def index():
    return "blablabla"
@app.route('/health', methods=['GET'])
def helth():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select 1;")
    rows = cursor.fetchall()
    resp = jsonify(rows)
    resp.status_code = 200
    return resp

@app.route('/item/<id>?from=t1&to=t2', methods=['GET'])
def itemId():
    

    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,age))
    mysql.connection.commit()
    cursor.close()


    resp = jsonify()
    resp.status_code = 404
    return resp   

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')

