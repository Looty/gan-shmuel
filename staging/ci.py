import os
from flask import Flask, request ,json
#import subprocess


app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    return "good"

@app.route('/health',methods=["GET"])
def health():
    return "ok"

@app.route('/gitcomm' , methods=['POST'])
def git_api_comm():
    if request.headers['Content-Type'] == 'application/json':
       
        my_commit = request.json
        jsonDump = json.dumps(my_commit)
        jsonLoad = json.loads(jsonDump)

        branch_ref = jsonLoad["ref"]

        directory_ref = jsonLoad["commits"][-1]

        branch = branch_ref.split("/")[2]
        print(branch)
        realDir = directory_ref["modified"]

        dirToString = str(realDir)
        realFolder = dirToString.split("/")[0]
        pureFolder = realFolder.replace("['","")
        
        print(pureFolder)
        os.system("echo $PWD")
        os.system("ls")
        os.system("cd /gan-shmuel/")
        os.system("echo $PWD")
        os.system("ls -a")
        os.system("git checkout origin/" + branch)
        os.system("git checkout " + branch)
        os.system("git pull")
        os.system("cd " + pureFolder)
        #os.system("pushd "+pureFolder)
        os.system("docker-compose up --detach")
        #os.system("popd")
        os.system("cd ../..")

        # subprocess.run(["git checkout", "origin/"+branch])
        # subprocess.run(["git pull"])
        # subprocess.run(["pushd", pureFolder])
        # subprocess.run(["docker-compose up --detach"])
        # subprocess.run(["popd"])
        return my_commit


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
