from flask import Flask, request ,json
import subprocess

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
        

        subprocess.run(["echo hello"])
        subprocess.run(["git checkout origin", branch], stderr=subprocess.PIPE, text=True)
        subprocess.run(["git pull"], stderr=subprocess.PIPE, text=True)
        subprocess.run(["pushd", pureFolder], stderr=subprocess.PIPE, text=True)
        subprocess.run(["docker-compose up --detach"], stderr=subprocess.PIPE, text=True)
        subprocess.run(["popd"], stderr=subprocess.PIPE, text=True)

        return my_commit


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
