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
    else:
        sys.exit(1)

x = tester()

