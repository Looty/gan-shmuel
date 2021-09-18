from os import error
import pymysql
from app import app
from db import mysql
import json
from flask import  jsonify,request
from datetime import datetime, date, time
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
@app.route("/batch-weight/<filename>", methods=['POST','GET'])
def POST_batch_weight(filename):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    filepath = f'./in/{filename}'
    query = f"INSERT INTO containers (id,weight,unit) VALUES (%s,%s,%s)"
    #case if it's JSON
    if filepath.endswith('.json'):
        with open(filepath,'r') as json_file:
            data = json.load(json_file)
            for line in data[1:]:
                weight = line['weight']
                id = line['id']
                unit = line['unit']
                values = (id, weight,unit)
                # return f"{id}    {weight}    {unit}"

                # cursor.execute(f"INSERT INTO containers (id,weight,unit) VALUES ({id},{weight},{unit})")
                cursor.execute(query , values)
        return f'The file {filename} was successfully added to the DB.'
        
    #case if it's CSV
    elif filepath.endswith('.csv'):
        with open(filepath,'r') as csv_file:
            data = csv_file.readlines()
            # unit = data[0].split(',')[1]
            unit = data[0][:-1].split(',')[1]
            if unit[0]=='"' and unit[-1]=='"':
                unit=unit[1:-1]
            for line in data[1:]:
                id = line.split(',')[0]
                weight = int(line.split(',')[1])
                values = (id,weight,unit)
                # return f"{id}    {weight}    {unit}"
                cursor.execute(query , values)
        return f'The file {filename} was successfully added to the DB.'
    else:
        return f'{filename} Error.'



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
    Filter = f"('{request.args.get('filter')}')" if request.args.get('filter') else "('in' , 'out' , 'none')" 
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
        #to fixxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        query=f"SELECT sessions_id FROM containers_has_sessions WHERE (SELECT date FROM sessions WHERE id=sessions_id) BETWEEN {_from} AND {_to};"
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
        cursor.execute(f"SELECT product_name FROM products WHERE id=(SELECT products_id FROM sessions WHERE id={id});")
        productname = cursor.fetchall()[0]["product_name"]
        if directionAnswer == "out":
            query=f"SELECT sessions.id, sessions.trucks_id AS truck, sessions.bruto,bruto-neto AS TruckTara, sessions.neto  FROM sessions WHERE sessions.id={id}"
            cursor.execute(query)
            result_list = cursor.fetchall()[0] 
        else:      
            query=f"SELECT id, trucks_id, bruto FROM sessions WHERE id={id}"
            cursor.execute(query)
            result_list = cursor.fetchall()[0] 
        result_list["product"]= productname    #return sql result
        resp = jsonify(result_list)
        resp.status_code = 200
        return resp
    except error as e:
        return "Error while connection to Mysql"


#77777777777777777777777777777777777777777777
@app.route("/weight", methods=['POST'])
def POST_weight():
    session_id=0
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # take all data
    direction=request.args.get('direction')
    containers=request.args.get('containers')
    weight=request.args.get('weight')
    unit=request.args.get('unit')
    force=request.args.get('force')
    product=request.args.get('product')
    truck_id=request.args.get('truckid')
    date = datetime.now().strftime('%Y%m%d%H%M%S')
    #pull out last direction
    #return str(f"{direction}  {containers}   {weight}   {unit}  {force}   {product}   {truck_id}   {date}")
    cursor.execute(f"SELECT direction FROM sessions WHERE trucks_id = {truck_id} ORDER BY date desc limit 1")
    result=cursor.fetchall()
    last_direction=result[0]["direction"]
    # return last_direction
    #neto
    cursor.execute(f'SELECT weight from containers WHERE id = "{containers}"')
    container_weight=cursor.fetchall()
    container_weight=container_weight[0]["weight"]
    truck_weight = cursor.execute(f'SELECT weight FROM trucks WHERE id = "{truck_id}"')
    truck_weight=cursor.fetchall()
    truck_weight=truck_weight[0]['weight']
    neto=float(weight)-container_weight-truck_weight
    #force=False - invalide direction
    if last_direction == direction and force == False :
        return f"Error direction for truck {truck_id}"
    #force=True - Weight overload
    elif last_direction == direction and force == True :
        cursor.execute(f'"UPDATE sessions SET bruto={weight} WHERE trucks_id={truck_id} ORDER BY date desc limit 1"')
    #none after in - Error
    elif direction == 'none' and last_direction == 'in':
        return f"Error direction for truck {truck_id}"
    elif direction == 'in' or direction == 'none':
        NewSession(str(direction), bool(force), date, float(weight), int(truck_id), str(product))
    elif direction == 'out':
        #out without - Error
        if last_direction != 'in':
            return f"Error direction for truck {truck_id}"
        cursor.execute(f'UPDATE sessions SET neto={neto} WHERE trucks_id={truck_id} AND direction="in" ORDER BY date desc limit 1 ')
        #retutn session id
        cursor.execute(f'SELECT id FROM sessions WHERE trucks_id={truck_id} AND direction="in" ORDER BY date desc limit 1')
        result=cursor.fetchall()
        session_id=result[0]['id']
        return f'session id: {session_id}'
    if direction == 'in' or direction == 'none':
            data = {
                "id": session_id,
                "truck": truck_id,
                "bruto": weight
            }
            return json.dumps(data)
    elif dir == 'out':
            data = {
                "id": session_id,
                "truck": truck_id,
                "bruto": weight,
                "truckTara": truck_weight,
                "neto": neto
            }
            return json.dumps(data)


def NewSession(direction, force, date, weight, truck_id, product):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f'SELECT id FROM products WHERE product_name="{product}" limit 1')
    product_id=cursor.fetchall()
    product_id=int(product_id[0]['id'])
    allData=(direction, force, date, weight, truck_id, product_id)
    query = (f'INSERT into sessions (direction, f, date, bruto, trucks_id, products_id) VALUES (%s, %s, %s, %s, %s, %s)')
    cursor.execute(query , allData)




if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')