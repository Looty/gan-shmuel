# this is a tessting script, meant to test all of the web routes of our project
import requests
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
    ret = checkPostResponse(baseRoute + "/provider?name=test1")
    provider_id1 =  str(ret["id"])
    ret = checkPostResponse(baseRoute + "/provider?name=test2")
    provider_id2 =  str(ret["id"])
    checkResponse(baseRoute + "/provider/" + provider_id2 + "?name=test3", "PUT")  
    # test truck functions
    ret = checkPostResponse(baseRoute + "/truck?provider_id=" + provider_id1 + "&id=101")
    ret = checkPostResponse(baseRoute + "/truck?provider_id=" + provider_id1 + "&id=102")
    truck_id2 = str(ret["id"])
    checkResponse(baseRoute + "/truck/" + truck_id2 + "?provider_id=" + provider_id2, "PUT")
    # test rates functions
    checkRatesResponse(baseRoute + "/rates?file=rates.csv")
    checkRatesResponse(baseRoute + "/rates?file=rates2.csv")
    checkRatesResponse(baseRoute + "/rates?file=rates3.csv")
    checkResponse(baseRoute + "/rates", "GET")
    sys.exit(0)


def checkPostResponse(route):
    print("testing " + route + "...", file=sys.stderr)
    response = requests.post(url=route)
    status_code = response.status_code
    json_dict = response.json()                 # print: {'id': 8}
    if status_code == 500:
        print(failure_msg, file=sys.stderr)
        sys.exit(1)
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


if __name__ == "__main__":
    main()
