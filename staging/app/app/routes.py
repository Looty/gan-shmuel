from flask import render_template, request
from app import app
import mysql.connector
import json


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/health', methods=['GET'])
def health():
    try:
        mydb = mysql.connector.connect(
            password='root', 
            user='root', 
            host='db', 
            database='billdb', 
            )
    
        mycursor = mydb.cursor()
        mycursor.execute("show tables")
        res = str(mycursor.fetchall())
    except:
        return render_template('health.html', msg='Something is broken.'), 500
    else:
        return render_template('health.html', msg=res), 200
 


@app.route('/provider', methods = ['POST', 'GET'])
def postProvide():
    if request.method == 'POST':
      id = request.form['id']
      name = request.form['name']
      with open('provider.json', 'r+') as f:
          feeds = json.load(f)
          feeds.append({"id":id, "name":name})
          f.seek(0)
          print(feeds)
          json.dump(feeds, f, indent="")
      return render_template('provider.html', msg=("provider id: %s added successfuly." %id))
    else:
      id = request.args.get('id')
      with open('provider.json', 'r') as f:
          feeds = json.load(f)
      return render_template('provider.html', msg=json.dumps(feeds))
