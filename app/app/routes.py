from flask import render_template, request, jsonify
from app import app
import mysql.connector
import sys
import json
import os

def init_db():
    return mysql.connector.connect(
        password='root', 
        user='root', 
        host='db', 
        database='billdb')
    
def to_json(cursor):
    headers = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return jsonify(list(map(lambda row: dict(zip(headers,row)) ,rows)))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/health', methods=['GET'])
def health():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        mycursor.execute("show tables")
        res = str(mycursor.fetchall())
    except:
        return render_template('health.html', msg='Something is broken.'), 500
    else:
        return render_template('health.html', msg=res), 200
 

@app.route('/provider', methods = ['POST'])
def postProvide():
        
    try:
        conn = init_db()
        mycursor2 = conn.cursor()
        Pname = request.args.get("name")
  
        sql = """INSERT INTO Provider (name) VALUES (%s)"""
        print (sql, file=sys.stderr)
        val = ([Pname])
        mycursor2.execute(sql, val)
        
    except Exception as inst:
        print(type(inst),file=sys.stderr)    # the exception instance
        print(inst.args,file=sys.stderr)     # arguments stored in .args
        return "db error", 500
    else:
        id = mycursor2.lastrowid
        retjson = {"id":id}
        return json.dumps(retjson, indent="")


@app.route('/provider/<id>', methods = ['PUT'])
def putProvide(id):    
    try:
        conn = init_db()
        mycursor2 = conn.cursor()
        Pname = request.args.get("name")
        sql = """UPDATE Provider SET name = %s WHERE id = %s"""
        print (sql, file=sys.stderr)
        val = ([Pname, id])
        mycursor2.execute(sql, val)
     
    except Exception as inst:
        print(type(inst),file=sys.stderr)    # the exception instance
        print(inst.args,file=sys.stderr)     # arguments stored in .args
        return "db error", 500
    else:
        return "on id: "+id + ", updated Provider name to : "+Pname


@app.route('/truck', methods = ['POST'])
def postTrucks():
        
    try:
        conn = init_db()
        mycursor3 = conn.cursor()
        Pid_in = request.args.get("id")
        Provider_id_in = request.args.get("provider_id")
        sql = """INSERT INTO Trucks (id, provider_id) VALUES (%s, %s)"""
        print (sql, file=sys.stderr)
        val = ([Pid_in, Provider_id_in])
        mycursor3.execute(sql, val)
        
    except Exception as inst:
        print(type(inst),file=sys.stderr)    # the exception instance
        print(inst.args,file=sys.stderr)     # arguments stored in .args
        return "db error", 500
    else:
        id = mycursor3.lastrowid
        retjson = {"id":id}
        return json.dumps(retjson, indent="")
    

@app.route('/truck/<id>', methods = ['PUT'])
def putTrucks(id):    
    try:
        conn = init_db()
        mycursor4 = conn.cursor()
        provider_id = request.args.get("provider_id")
        sql = """UPDATE Trucks SET provider_id = %s WHERE id = %s"""
        print (sql, file=sys.stderr)
        val = ([provider_id, id])
        mycursor4.execute(sql, val)
     
    except Exception as inst:
        print(type(inst),file=sys.stderr)    # the exception instance
        print(inst.args,file=sys.stderr)     # arguments stored in .args
        return "db error", 500
    else:
        return "on id: "+id + ", updated id to : "+provider_id 


@app.route('/rates', methods = ['POST'])
def postRates():
    try:
        conn = init_db()
        mycursor5 = conn.cursor()
        sql = """DELETE FROM Rates"""
        print (sql, file=sys.stderr)
        mycursor5.execute(sql)
        
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
            mycursor5.executemany(sql, map(lambda r: [r["Product"], r["Rate"], r["Scope"]], rates))
            
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
        mycursor6 = conn.cursor()
        mycursor6.execute("SELECT product_id,rate,scope FROM Rates")
        return to_json(mycursor6)

    except Exception as inst:
        print(type(inst),file=sys.stderr)    # the exception instance
        print(inst.args,file=sys.stderr)     # arguments stored in .args
        return "db error", 500
