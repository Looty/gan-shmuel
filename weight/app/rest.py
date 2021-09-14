from os import error
import pymysql
from app import app
from db import mysql
from flask import jsonify,request
from datetime import datetime, date
@app.route('/')
def users():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id FROM containers")
    rows = cursor.fetchall()
    resp = jsonify(rows)
    resp.status_code = 200
    return resp

#111111111111111111111111111111111111111
@app.route("/health", methods=['GET'])
def health():
    return 'ok'
    
#222222222222222222222222222222222222222


#333333333333333333333333333333333333333    
@app.route("/unknown", methods=['GET'])
def unknown():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT distinct id FROM containers WHERE weight IS NULL")
    rows = cursor.fetchall()
    resp = jsonify(rows)
    resp.status_code = 200
    return resp

#444444444444444444444444444444444444
def enum(**enums):
    return type('Enum', (), enums) 
@app.route("/weight" , methods=['GET'])
def GET_weight():
    conn= mysql.connect()
    cursor=conn.cursor(pymysql.cursors.DictCursor)
 
    fromTime = request.args.get('from') if request.args.get('from') else datetime.now().strftime("%Y%m%d000000") 
    toTime = request.args.get('to') if request.args.get('to') else datetime.now().strftime("%Y%m%d%H%M%S") 
    Filter = f"('{request.args.get('filter')}')" if request.args.get('filter') else "('in', 'out', 'none')" 
    query="""SELECT t1.id, direction, bruto, neto, product_name, GROUP_CONCAT(t3.containers_id) as containers 
    FROM sessions AS t1 JOIN products AS t2 ON t1.products_id = t2.id 
    JOIN containers_has_sessions as t3 ON t1.id = t3.sessions_id 
    WHERE t1.date BETWEEN '{0}' AND '{1}' AND direction IN {2} 
    GROUP BY t3.sessions_id""" 
    cursor.execute(query.format(fromTime,toTime,Filter))
    # cursor.execute(query)
    rows = cursor.fetchall()
    resp = jsonify(rows)
    resp.status_code = 200
    return resp

#555555555555555555555555555555555555555    
@app.route('/item/<id>', methods=['GET'])
def itemId(id):
    now = datetime.now()
    time = now.strftime("%Y%m")
    test_id = id
    _from = request.args.get('from')
    _to = request.args.get('to')
    if not _to:
        _to = now.strftime("%Y%m%d%H%M%S")
        # _to=11111111111111
    if not _from:
        _from = time + '01000000'
        # _from=88888888888888
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        int_id=int(id)
        query=f"SELECT DISTINCT neto FROM sessions WHERE date=(SELECT MAX(date) FROM sessions WHERE trucks_id={int_id});"
        cursor.execute(query) 
        netoCursor = cursor.fetchall()
        query_sessions=f"SELECT id FROM sessions WHERE trucks_id={int_id} AND date BETWEEN {_from} AND {_to};"
        cursor.execute(query_sessions) 
        rows=[] 
        rows = cursor.fetchall()
        session={
        "id":0,
        "tara":0,
        }
        if not rows:
            session["id"] = 404,
            session["tara"] = 'N/A' 
        else:
            session = { 
            "id":int(test_id),
            "tara":netoCursor[0],
            "sessions":[]
            }  
            for i in range(0, len(rows)):
                 session["sessions"].append(rows[i]["id"])
        resp = jsonify(session)
        resp.status_code = 200
        return resp
    except:
        getContainerWeight=f"SELECT weight FROM containers WHERE id='{test_id}';"
        cursor.execute(getContainerWeight) 
        ContainerWeight = cursor.fetchall()
        query=f"SELECT sessions_id FROM containers_has_sessions WHERE containers_id='{test_id} AND date BETWEEN {_from} AND {_to}';"
        cursor.execute(query)
        rows=[] 
        rows = cursor.fetchall()
        session={
        "id":0,
        "tara":0,
        }
        if not rows:
            session["id"] = 404,
            session["tara"] = 'N/A' 
        else:
            session = { 
            "id":test_id,
            "tara":ContainerWeight[0],
            "sessions":[]
            } 
            for i in range(0, len(rows)):
                 session["sessions"].append(rows[i]["sessions_id"])
        resp = jsonify(session)
        resp.status_code = 200
        return resp
    
#666666666666666666666666666666666666666666    
@app.route('/session/<id>',methods=['GET'])
def GET_session(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        direction=f"SELECT direction FROM sessions WHERE id={id}"
        cursor.execute(direction)
        directionAnswer = cursor.fetchall()    
        directionAnswer = directionAnswer[0]["direction"]
        if directionAnswer == "out":
            query=f"SELECT sessions.id, sessions.trucks_id AS truck, sessions.bruto,bruto-neto AS TruckTara, sessions.neto  FROM sessions WHERE sessions.id={id}"
            cursor.execute(query)
            result_list = cursor.fetchall() 
        else:      
            query=f"SELECT id, trucks_id AS truck, bruto FROM sessions WHERE id={id}"
            cursor.execute(query)
            result_list = cursor.fetchall()      #return sql result
        resp = jsonify(result_list[0])
        resp.status_code = 200
        return resp
    except error as e:
        return "Error while connection to Mysql"

#77777777777777777777777777777777777777777777
    
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')