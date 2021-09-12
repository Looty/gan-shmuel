import sys

# ...
# ...
# ...
# ...

test = "OK"
def tester():
    if test == "OK":
        #print("All test passed!")
        sys.exit(0)
        #os.system("python rest.py")
    else:
        #print("A test failed! the server was not started!")
        sys.exit(1)

x = tester()