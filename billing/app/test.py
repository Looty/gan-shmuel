# this is a tessting script, meant to test all of the web routes of our project
import requests, mysql.connector
import sys


domain = "http://localhost"
port = 5000
baseRoute = domain + ":" + str(port)
failure_msg = "something went wrong."


def main():
    # test simple GET functions
    checkResponse(baseRoute + "/health", "GET")
    checkResponse(baseRoute + "/billing", "GET")
    checkResponse(baseRoute + "/index", "GET")
    # test provider functions
    ret1 = checkPostResponse(baseRoute + "/provider?name=test1")
    provider_id1 =  str(ret1["id"])
    ret2 = checkPostResponse(baseRoute + "/provider?name=test2")
    provider_id2 =  str(ret2["id"])
    checkResponse(baseRoute + "/provider/" + provider_id2 + "?name=test3", "PUT")
    # test truck functions
    ret3 = checkPostResponse(baseRoute + "/truck?provider_id=" + provider_id1 + "&id=101")
    truck_id1 = str(ret3["id"])
    ret4 = checkPostResponse(baseRoute + "/truck?provider_id=" + provider_id1 + "&id=102")
    truck_id2 = str(ret4["id"])
    checkResponse(baseRoute + "/truck/" + truck_id2 + "?provider_id=" + provider_id2, "PUT")
    # test rates functions
    checkRatesResponse(baseRoute + "/rates?file=rates2.csv")
    checkResponse(baseRoute + "/rates", "GET")
    checkRatesResponse(baseRoute + "/rates?file=rates3.csv")
    checkResponse(baseRoute + "/rates", "GET")
    checkRatesResponse(baseRoute + "/rates?file=rates.csv")
    checkResponse(baseRoute + "/rates", "GET")
    # delete all changes from 'Provider' and 'Trucks' tables
    undoChanges(provider_id1, provider_id2, truck_id1, truck_id2)
    sys.exit(0)


def checkPostResponse(route):
    print("testing " + route + "...", file=sys.stderr)
    response = requests.post(url=route)
    status_code = response.status_code
    if status_code == 500:
        print(failure_msg, file=sys.stderr)
        sys.exit(1)
    else:
        json_dict = response.json()                 # print: {'id': 8}
    return json_dict


def checkRatesResponse(route):
    print("testing " + route + "...", file=sys.stderr)
    if requests.post(url=route).status_code == 500:
        print(failure_msg, file=sys.stderr)
        sys.exit(1)


def checkResponse(route, method):
    print("testing " + route + "...", file=sys.stderr)
    status_code = requests.put(route).status_code if method == "PUT" else requests.get(route).status_code
    if status_code == 500:
        print(failure_msg, file=sys.stderr)
        sys.exit(1)


def undoChanges(provider_id1, provider_id2, truck_id1, truck_id2):
    conn = mysql.connector.connect(
                                    password='root', 
                                    user='root', 
                                    host='bdb', 
                                    database='billdb'
                                )
    mycursor = conn.cursor()
    sql = """DELETE FROM Provider WHERE id=%s"""
    mycursor.execute(sql, [provider_id1])
    mycursor.execute(sql, [provider_id2])
    sql = """DELETE FROM Trucks WHERE id=%s"""
    mycursor.execute(sql, [truck_id1])
    mycursor.execute(sql, [truck_id2])


if __name__ == "__main__":
    main()
