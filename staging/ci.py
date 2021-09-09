from flask import Flask, request ,json, jsonify
import json
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
        myJson = json.dumps(my_commit, indent=4)
        
        #r = json.parse(my_commit)
        #r = jsonify(my_commit)

        print(myJson)

        branch_ref = myJson.ref

        print(branch_ref)

        directory_ref = myJson.commits["modified"]

        print(directory_ref)
        
        branch = branch_ref.split("/")[2]

        print(branch)

        directory = directory_ref.split("/")[0]

        print(directory)

        subprocess.run(["echo hello"])
        subprocess.run(["git checkout origin", branch], stderr=subprocess.PIPE, text=True)
        subprocess.run(["git pull"], stderr=subprocess.PIPE, text=True)
        subprocess.run(["pushd", directory], stderr=subprocess.PIPE, text=True)
        subprocess.run(["docker-compose up --detach"], stderr=subprocess.PIPE, text=True)
        subprocess.run(["popd"], stderr=subprocess.PIPE, text=True)

        return my_commit


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
