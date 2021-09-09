from flask import render_template
from app import app
from flask import request
import mysql.connector
from mysql.connector import Error 

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/health', methods=['GET'])
def health():
    
    mydb = mysql.connector.connect(
        password='root', 
        user='root', 
        host='db', 
        port='3306', 
        database='billdb' , 
        auth_plugin='mysql_native_password')
    
    mycursor = mydb.cursor()
    mycursor.execute("show tables")
    res = str(mycursor.fetchall()) 
    if res:
        return '<h1>It works.</h1>'
    else:
        return '<h1>Something is broken.</h1>'
 
