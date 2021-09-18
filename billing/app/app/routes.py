#change this to generate commit, fun counter: 4
from flask import render_template, request, jsonify
import requests
from app import app
import mysql.connector, sys, json, os, datetime, random, csv, re
import traceback

# initialize connection to database 'billdb', in mysql server
def init_db():
    return mysql.connector.connect(
        password='root', 
        user='root', 
        host='bdb', 
        database='billdb'
    )


# default page of the application
@app.route('/')
@app.route('/billing')
def billing():
    return render_template('billing.html', title='Home')


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
        if not isinstance(val[0], str) or len(val[0])>255:
            return "bad type or length inserted", 400
        # check if the name already exist in the database
        sql = """SELECT * FROM Provider WHERE name=%s"""
        mycursor.execute(sql, val)
        if mycursor.fetchone():
            return "name already exist", 422
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
        # check if the input id and provider_id are valid
        if not isinstance(id, str) or len(id)>10 or re.findall("\D", provider_id) or len(provider_id)>11:
            return "bad type or length inserted", 400
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
            return "truck license plate: " + id + " already exist", 422
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
        file = os.path.join(".","in", filename)
        #file = os.path.join("..","in", filename)
        if not os.path.isfile(file):
            return "file: " + filename + " does not exist inside /in directory", 404
        if not filename.endswith('.csv'):
            return "please post csv files only. ", 400
        with open (file, "r" ) as csv_file:
            # rates is list of lists: [['Navel', '93', 'All'], ['Blood', '112', 'All'], ['Mandarin', '104', 'All'], ...]
            rates = list(csv.DictReader(csv_file))
            if len(rates[0]) < 3:
                return "error in reading file. make sure the file has at least 3 columns", 400
        try:
            sql = """INSERT INTO Rates (product_id, rate, scope) VALUES (%(Product)s, %(Rate)s, %(Scope)s)"""
            mycursor.executemany(sql, rates)
        except:
            return "error in reading file. USAGE: ""<Product (str)>, <Rate (int)>, <Scope (str)>""", 400
    except:
        return "db error", 500
    else:
        return "rates table updated successfully",200


# get all rates from the 'Rates' table as json object
@app.route('/rates', methods=['GET'])
def getRates():
    try:
        conn = init_db()
        mycursor = conn.cursor(dictionary=True)
        mycursor.execute("SELECT product_id,rate,scope FROM Rates")
        rows = mycursor.fetchall()
        if not rows:
            return "Rates table is empty!", 400
    except Exception as inst:
        return "db error", 500
    else:
        # convert mysql table into dictionary and then to json response objec
        return jsonify(rows), 200



session_cache = dict() # global session_cache
truck_list = ("1111111","2222222","3333333","4444444","5555555","6666666")
@app.route('/session/<id>', methods=['GET'])
def getSession(id):
    if len(session_cache) == 0:
        createSessions()
    
    if int(id) in session_cache:
        return jsonify(session_cache[int(id)]), 200
    return "session not found", 404
    
def createSessions():
    for i in range(len(truck_list)):
        for j in range(5):
            id = i*5+j+1
            product_list = ["Mandarin", "Blood", "Grapefruit","Navel","Shamuti"]
            session =  { "id": id, 
                "truck": random.choice(truck_list),
                "bruto": random.randint(30, 70),
                "product": random.choice(product_list),
                "neto": random.randint(10, 50)
            }
            session_cache[id] = session


truck_session_cache = dict() #global truck_
@app.route('/item/<license_id>', methods=['GET'])
def getItem(license_id):
    if license_id in truck_session_cache:
        return jsonify(truck_session_cache[license_id]), 200
    
    sess_list =[]
    company_num_list = [234, 753,634,125,634,243,100]
    if not license_id in truck_list:
        return "truck not found", 404

    if len(session_cache) == 0:
        createSessions() # init dummy sessions, happens only once

    ###  session_cache.items() -> creates a list of tuples, each tuple gets session id and session
    ### lambda item: item[1]["truck"] == license_id -> [1] to take the session and not the key,finds the sessions with "truck":license_id
    ### map takes all the sessions from the tuples
    sess_list = list(map(lambda item: item[1],filter(lambda item: item[1]["truck"] == license_id, session_cache.items())))
    retjson = { "id": license_id,
        "comapny": random.choice(company_num_list),
        "sessions": list(map(lambda s: s["id"], sess_list))
    }
    truck_session_cache[license_id] = retjson
    return jsonify(retjson), 200


@app.route('/truck/<license_id>', methods=['GET'])
def getTruck(license_id):
    return getItem(license_id)


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
        if not provider_name:
            return "provider not exist", 404
        
        mycursor.execute("""SELECT id FROM Trucks WHERE provider_id=%s""" % (id))
        licenses_set = list(sum(mycursor.fetchall(), ()))
        sessions_list = []
        for license in licenses_set:
            items = getItem(license)[0]
            dict_data = items.json
            sessions_list.extend(dict_data["sessions"])
        sessions_count = len(sessions_list)
        truck_list = []
        product_data = dict()
        
        for sess in sessions_list:
            sess_data = getSession(sess)[0].json #takes the data from current session
            truck_list.append(sess_data["truck"]) # adds the truck to a list, that will be "set" later for unique values
            
            if not sess_data["product"] in product_data:
                product_data[sess_data["product"]] = {
                                        "product":sess_data["product"],
                                        "count":1,
                                        "amount":sess_data["neto"]
                                    }
            else:
                product_information = product_data[sess_data["product"]]
                product_information["count"]+=1
                product_information["amount"]+=sess_data["neto"]
                                        
        total = 0
        for product_id in product_data:
            try:    
                mycursor.execute("""SELECT rate FROM Rates WHERE product_id=%s
                                and (scope=%s OR scope = 'All') order by scope='All' LIMIT 1""",(product_id,id))
            ## WHERE product_id=%s and (scope=%s OR scope = 'All') order by scope='All' LIMIT 1
            ## -> try to find All the provider id, orders the results as "All"s are last, so provider id's will be found first
                product_rate = mycursor.fetchone()[0]
            except Exception as inst:
                return "no rate table in use!", 400  
                
            product_data[product_id]["rate"] = product_rate
            product_data[product_id]["pay"] = product_rate* product_information["amount"]
            total+=product_data[product_id]["pay"]
        
        
        truck_count = len(set(truck_list)) 
        ret_dict = {
            'id': id,
            'name': provider_name[0],
            'from': t1,
            'to': t2,
            'truckCount': truck_count,
            'sessionCount': sessions_count,
            'products': list(product_data.values()),
            'total': total
        }
    except Exception as inst:
        traceback.print_exc()
        return "db error", 500
    else:
        return jsonify(ret_dict), 200
