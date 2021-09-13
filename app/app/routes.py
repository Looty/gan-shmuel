from flask import render_template, request, jsonify
import requests
from app import app
import mysql.connector
import sys
import json
import os
import datetime


# initialize connection to database 'billdb' in mysql server
def init_db():
    return mysql.connector.connect(
        password='root', 
        user='root', 
        host='db', 
        database='billdb')


# convert mysql table into json response objec
def to_json(cursor):
    headers = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return jsonify(list(map(lambda row: dict(zip(headers,row)) ,rows)))


# default page of the application
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


# check if connection to the database established successfully
@app.route('/health', methods=['GET'])
def health():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        mycursor.execute("show tables")
        # res stores the output of the last executed command
        res = str(mycursor.fetchall())
    except:
        return render_template('health.html', msg='Something is broken.'), 500
    else:
        return render_template('health.html', msg=res), 200


# create a new provider element (id, name) and insert it to the 'Provider' table in the database
@app.route('/provider', methods = ['POST'])
def postProvider():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        # execute: insert 'name' into 'Provider' table (id created automatically)
        sql = """INSERT INTO Provider (name) VALUES (%s)"""
        val = ([request.args.get("name")])
        mycursor.execute(sql, val)
        id = mycursor.lastrowid
        retjson = {"id":id}
    except:
        return "db error", 500
    else:
        print("provider '" + request.args.get("name") + "' added with the id: " + str(id), file=sys.stderr)
        return json.dumps(retjson, indent=""), 200


# update a provider element (id, name) in the 'Provider' table in the database 
@app.route('/provider/<id>', methods = ['PUT'])
def putProvide(id):    
    try:
        conn = init_db()
        mycursor = conn.cursor()
        # execute: update the 'name' of the wanted provider id ('id') in the 'Provider' table
        sql = """UPDATE Provider SET name = %s WHERE id = %s"""
        val = ([request.args.get("name"), id])
        mycursor.execute(sql, val)
    except:
        return "db error", 500
    else:
        return "on id: " + str(id) + ", updated Provider name to : " + request.args.get("name"), 200


# create a new truck element (id, provider_id) and insert it to the 'Trucks' table in the database
@app.route('/truck', methods = ['POST'])
def postTrucks():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        id = request.args.get("id")
        # execute: insert 'id' and 'provider_id' into 'Trucks' table
        sql = """INSERT INTO Trucks (id, provider_id) VALUES (%s, %s)"""
        val = ([id, request.args.get("provider_id")])
        mycursor.execute(sql, val)
        retjson = {"id":id}
    except:
        return "db error", 500
    else:
        return json.dumps(retjson, indent=""), 200
    

# update a truck element (id, provider_id) in the 'Trucks' table in the database
@app.route('/truck/<id>', methods = ['PUT'])
def putTrucks(id):    
    try:
        conn = init_db()
        mycursor = conn.cursor()
        sql = """UPDATE Trucks SET provider_id = %s WHERE id = %s"""
        val = ([request.args.get("provider_id"), id])
        mycursor.execute(sql, val)
    except:
        return "db error", 500
    else:
        return "on id: " + id + ", updated id to : " + request.args.get("provider_id"), 200


# update 'Rates' table in the database, from a .csv file
@app.route('/rates', methods = ['POST'])
def postRates():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        # delete all the rows 
        sql = """DELETE FROM Rates"""
        mycursor.execute(sql)
        filename = request.args.get("file")
        filename = os.path.join("..","in", filename)
        rates = []
        if os.path.isfile(filename):
            with open (filename, "r" ) as exelfile:
                lines = exelfile.readlines()
                headers = lines[0][:-1].split(",")
                for line in lines[1:]:
                    row = dict()
                    values = line[:-1].split(",")
                    for i in range(len(headers)):
                        row[headers[i]] = values[i] 
                    rates.append(row)
            sql = """INSERT INTO Rates (product_id, rate, scope) VALUES (%s, %s, %s)"""
            mycursor.executemany(sql, map(lambda r: [r["Product"], r["Rate"], r["Scope"]], rates))
    except Exception as inst:
        print(type(inst),file=sys.stderr)    # the exception instance
        print(inst.args,file=sys.stderr)     # arguments stored in .args
        return "db error", 500
    else:
        return "rates updated",200


@app.route('/rates', methods=['GET'])
def getRates():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        mycursor.execute("SELECT product_id,rate,scope FROM Rates")
    except Exception as inst:
        return "db error", 500
    else:
        return to_json(mycursor), 200


@app.route('/session/<id>', methods=['GET'])
def getSession(id):
    retjson =  { "id": id, 
                "truck": "22222",
                "bruto": 47,
                "truckTara": 40,
                "neto": 7
                }
    return json.dumps(retjson, indent=""), 200


@app.route('/truck/<license_id>', methods=['GET'])
def getTruck(license_id):
    response = requests.get("http://localhost:5000/item/" + license_id)
    ret = response.json()
    return jsonify(ret), 200


@app.route('/item/<id>', methods=['GET'])
def getItem(id):
    retjson = { "id": id,
                "hody5": 7,
                "sessions": [1,2,3,4,5]
            }
    return jsonify(retjson), 200


@app.route('/bill/<id>', methods=['GET'])
def getBill(license_id):
    # get the time parameters
    t1 = request.args.get("from") if "from" in request.args else datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0).strftime('%Y%m%d%H%M%S')
    t2 = request.args.get("to") if "to" in request.args else datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    print(t1,file=sys.stderr)
    print(t2,file=sys.stderr)

    try:
        conn = init_db()
        mycursor = conn.cursor()
        # check if the license id of the truck exsist in the database
        mycursor.execute("""SELECT * FROM Trucks WHERE id=%s""" % (license_id))
        if not mycursor.fetchone():
            return "not exist.", 404
        # get the provider_id from the 'Trucks' table, and provider_name from the 'Provider' table
        mycursor.execute("""SELECT provider_id FROM Trucks WHERE id=%s""" % (license_id))
        provider_id = mycursor.fetchone()
        mycursor.execute("""SELECT name FROM Provider WHERE id=%s""" % (provider_id))
        provider_name = mycursor.fetchone() # tuple (5,)
        # get a single session from /session/<id>
        session = getSession(license_id)
        # get the weights from the session
        weight = json.loads(session[0].replace("'", "\"").replace("\n", ""))["neto"]
        # create a dictionary with the return values
        ret_dict = {"id":license_id, "provider_name":weight, "sessions":session}

        mycursor.execute("SELECT * FROM Trucks")
        res = mycursor.fetchall()
    except Exception as inst:
        print(type(inst),file=sys.stderr)
        print(inst.args,file=sys.stderr)
        return "db error", 500
    else:
        return str(res), 200
