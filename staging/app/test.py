import sys
# ...
# ...
# ...
# ...
test = "OK"
def tester():
    if test == "OK":
        #print("All test passed!")
        return "OK"
        #os.system("python rest.py")
    else:
        #print("A test failed! the server was not started!")
        return "ERROR"
x = tester()