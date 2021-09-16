from flask import render_template, request, jsonify
from pip._vendor import requests
from app import app
import mysql.connector, sys, json, os, datetime, random


# initialize connection to database 'billdb' in mysql server
def init_db():
    return mysql.connector.connect(
        password='root', 
        user='root', 
        host='bdb', 
        database='billdb'
    )


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
        res = str(mycursor.fetchall())
    except:
        return "failed connecting to the database", 500
    else:
        return render_template('health.html', msg=res), 200


# create a new provider element (id, name) and insert it to the 'Provider' table in the database
@app.route('/provider', methods = ['POST'])
def postProvider():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        val = [request.args.get("name")]
        # check if the input name is valid
        if not isinstance(val[0], str) or len(val)>255:
            return "bad type or length inserted", 400
        # check if the name already exist in the database
        sql = """SELECT * FROM Provider WHERE name=%s"""
        mycursor.execute(sql, val)
        if mycursor.fetchone():
            return "name already exist", 400
        # execute: insert 'name' into 'Provider' table (id created automatically)
        sql = """INSERT INTO Provider (name) VALUES (%s)"""
        mycursor.execute(sql, val)
        id = mycursor.lastrowid
        if not id:
            return "inserting new name failed", 500
        retjson = {
                    "id": id
                }
    except:
        return "db error", 500
    else:
        return jsonify(retjson), 200


# update a provider element (id, name) in the 'Provider' table in the database 
@app.route('/provider/<id>', methods = ['PUT'])
def putProvider(id):    
    try:
        conn = init_db()
        mycursor = conn.cursor()
        provider_name = request.args.get("name")
        # check if the provider id exist
        sql = """SELECT * FROM Provider WHERE id=%s"""
        mycursor.execute(sql, [id])
        res = mycursor.fetchone()                           # res is a tuple: (id, 'name')
        msg = ""
        if not res:
            return "provider id " + id +" doesn't exist.", 400
        elif res[1] == provider_name:
            msg = " already exist."
        else:
            # execute: update the 'name' of the wanted provider id ('id') in the 'Provider' table
            sql = """UPDATE Provider SET name = %s WHERE id = %s"""
            val = [provider_name, id]
            mycursor.execute(sql, val)
            msg = " updated."
    except:
        return "db error", 500
    else:
        return "on id: " + str(id) + " Provider name: " + provider_name + msg, 200


# create a new truck element (id, provider_id) and insert it to the 'Trucks' table in the database
@app.route('/truck', methods = ['POST'])
def postTrucks():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        id = request.args.get("id")
        provider_id = request.args.get("provider_id")
        val = [id, provider_id]
        # check if the given provider id exist
        sql = """SELECT * FROM Provider WHERE id=%s"""
        mycursor.execute(sql, [provider_id])
        provider_res = mycursor.fetchone()
        if not provider_res:
            return "provider id " + provider_id +" doesn't exist.", 400
        # check if the truck id already exist
        sql = """SELECT * FROM Trucks WHERE id=%s"""
        mycursor.execute(sql, [id])
        truck_res = mycursor.fetchone()
        if truck_res:
            return "truck license plate: " + id + " already exist", 200
        # execute: insert 'id' and 'provider_id' into 'Trucks' table
        sql = """INSERT INTO Trucks (id, provider_id) VALUES (%s, %s)"""
        mycursor.execute(sql, val)
        retjson = {
                    "id": id,
                    "provider id": provider_id
                }
    except:
        return "db error", 500
    else:
        return jsonify(retjson), 200
    
# select * from Trucks, Provider where Trucks.provider_id=Provider.id and Provider.id=3;

# update a truck element (id, provider_id) in the 'Trucks' table in the database
@app.route('/truck/<id>', methods = ['PUT'])
def putTrucks(id):    
    try:
        conn = init_db()
        mycursor = conn.cursor()
        provider_id = request.args.get("provider_id")
        # check if the given provider id exist
        sql = """SELECT * FROM Provider WHERE id=%s"""
        mycursor.execute(sql, [provider_id])
        provider_res = mycursor.fetchone()
        if not provider_res:
            return "provider id " + provider_id +" doesn't exist.", 400
        # check if the truck id exist
        sql = """SELECT * FROM Trucks, Provider WHERE Trucks.provider_id=Provider.id AND Trucks.id=%s"""
        mycursor.execute(sql, [id])
        truck_res = mycursor.fetchone()
        if not truck_res:
            return "truck license plate " + id + " doesn't exist.", 400
        # check if the provider id hasn't changed
        previos_provider = str(truck_res[2])
        if previos_provider == provider_id:
            return "provider id: " + provider_id + " is already up to date.", 200
        # update the truck's provider id
        sql = """UPDATE Trucks SET provider_id = %s WHERE id = %s"""
        val = ([provider_id, id])
        mycursor.execute(sql, val)
    except:
        return "db error", 500
    else:
        return "on truck id: " + id + ", updated provider from: " + previos_provider +  " to: " + provider_id, 200


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
        if not os.path.isfile(filename):
            return "file does not exist inside /in directory", 400
        # rates is list of lists: [['Navel', '93', 'All'], ['Blood', '112', 'All'], ['Mandarin', '104', 'All'], ...]
        rates = []
        with open (filename, "r" ) as csv_file:
            lines = csv_file.readlines()
            for line in lines[1:]:
                values = line[:-1].split(",")
                rates.append([values[0], values[1], values[2]])
            sql = """INSERT INTO Rates (product_id, rate, scope) VALUES (%s, %s, %s)"""
            mycursor.executemany(sql, rates)
    except:
        return "db error", 500
    else:
        return "rates table updated successfully",200


@app.route('/rates', methods=['GET'])
def getRates():
    try:
        conn = init_db()
        mycursor = conn.cursor()
        mycursor.execute("SELECT product_id,rate,scope FROM Rates")
        headers = [col[0] for col in mycursor.description]
        rows = mycursor.fetchall()
    except Exception as inst:
        return "db error", 500
    else:
        # convert mysql table into dictionary and then to json response objec
        return jsonify(list(map(lambda row: dict(zip(headers,row)) ,rows))), 200


@app.route('/session/<id>', methods=['GET'])
def getSession(id):
    truc_list = ["101", "102", "105", "101", "105"]
    retjson =  { "id": id, 
                "truck": random.choice(truc_list),
                "bruto": 47,
                "Mandarin": 20,
                "neto": random.randint(10, 50)
                }
    return jsonify(retjson), 200


@app.route('/item/<license_id>', methods=['GET'])
def getItem(license_id):
    sess_list =[]
    for i in range(3):
        sess = getSession(1)[0]
        dict_data = json.loads(sess.data.decode('utf-8'))
        sess_list.append(dict_data)
    retjson = { "id": license_id,
                "hody5": 1,
                "sessions": sess_list
            }
    return jsonify(retjson), 200


@app.route('/truck/<license_id>', methods=['GET'])
def getTruck(license_id):
    try:
        conn = init_db()
        mycursor = conn.cursor()
        # check if the license id of the truck exsist in the database
        mycursor.execute("""SELECT * FROM Trucks WHERE id=%s""" % (license_id))
        if not mycursor.fetchone():
            return "not exist.", 404
        response = requests.get("http://localhost:5000/item/" + license_id)
        ret = response.json()
    except:
        return "something is wrong.", 500
    else:
        return jsonify(ret), 200


@app.route('/bill/<id>', methods=['GET'])
def getBill(id):
    # get the time parameters
    t1 = request.args.get("from") if "from" in request.args else datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0).strftime('%Y%m%d%H%M%S')
    t2 = request.args.get("to") if "to" in request.args else datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    try:
        conn = init_db()
        mycursor = conn.cursor()
        # get the provider_name from the 'Provider' table
        mycursor.execute("""SELECT name FROM Provider WHERE id=%s""" % (id))
        provider_name = mycursor.fetchone() # tuple (5,)
        mycursor.execute("""SELECT id FROM Trucks WHERE provider_id=%s""" % (id))
        licenses_set = list(sum(mycursor.fetchall(), ())) # from tuple: [("101",),  ("105",), ....] to list []
        print(licenses_set,file=sys.stderr)
        sessions_list = []
        for license in licenses_set:
            items = getTruck(license)[0]
            dict_data = json.loads(items.data.decode('utf-8'))
            sessions_list.extend(dict_data["sessions"])
        sessions_count = len(sessions_list)
        truck_list = []
        for sess in sessions_list:
            truck_list.append(sess["truck"])
        truck_count = len(set(truck_list))
        print("****************",file=sys.stderr)
        print(sessions_list,file=sys.stderr)
        print(truck_list,file=sys.stderr)
        
        # create a dictionary to be return
        ret_dict = {
            'id': id,
            'name': provider_name,
            'from': t1,
            'to': t2,
            'truckCount': truck_count,
            'sessionCount': sessions_count,
            'products': [{
                'product': 'orange',
                'count': '5',
                'amount': 100,
                'rate': 20,
                'pay': 2000
                }],
            'total': 50
        }
        print(ret_dict,file=sys.stderr)
        mycursor.execute("SELECT * FROM Trucks")
        res = mycursor.fetchall()
    except Exception as inst:
        print(type(inst),file=sys.stderr)
        print(inst.args,file=sys.stderr)
        return "db error", 500
    else:
        return str(res), 200

# trucks table: id, provider_id
# set_of_trucks_for_id = (...)
# for loop: getTruck(license_id) for each one in set_of_trucks_for_id from t1 to t2
# insert each session from getTruck(license_id)[sessions] into sessions_list
# sessions_list = [...]
# truck_id_list =[...]
# truckCount = len(set(truck_id_list))

# {
#   "id": <str>,
#   "name": <str>,
#   "from": <str>,
#   "to": <str>,
#   "truckCount": <int>,
#   "sessionCount": <int>,
#   "products": [
#     { "product":<str>,   product_id from Rates table
#       "count": <str>, // number of sessions
#       "amount": <int>, // total kg
#       "rate": <int>, // agorot
#       "pay": <int> // agorot
#     },...
#   ],
#   "total": <int> // agorot
# }

        # get a single session from /session/<id>
        # session = getSession(id)
        # get the weights from the session
        # weight = json.loads(session[0].replace("'", "\"").replace("\n", ""))["neto"]



# if conn.is_connected():
#         cursor = conn.cursor()
#         cursor.execute("CREATE DATABASE employee")


# print(type(inst),file=sys.stderr)    # the exception instance
# print(inst.args,file=sys.stderr)     # arguments stored in .args