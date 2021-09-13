import pymysql
from app import app
#from db import mysql
from flask import jsonify
import mysql.connector
from mysql.connector import Error

@app.route('/')
def users():
    return 'ok'


@app.route("/health", methods=['GET'])
def health():
    return 'ok'

@app.route("/unknown", methods=['GET'])
def unknown():
    return 'ok'

@app.route('/weight', methods=['GET'])
def weigtPost():
    # def GET_unknown():
    try:
            connection = mysql.connector.connect(host='db',database='roytuts',user='root',password='123456')
            if (connection.is_connected()):
                SQL = "SELECT * FROM containers;"
                cursor = connection.cursor()
                cursor.execute(SQL)
                result_list = cursor.fetchall()      #return sql result
                return '\n'.join(map(str,result_list)) #is s list type, need to be a dict
                fields_list = cursor.description   # sql key name
                return ("fields result -->",type(fields_list))
                #print("header--->",fields)
                cursor.close()
                connection.close()
    except Error as e:
        return "bbb"





if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
