from flask import Flask, request , json
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

        '''branch_ref = my_commit.ref
        directory_ref = my_commit.commits["modified"]
        
        branch = branch_ref.split("/")[2]
        directory = directory_ref.split("/")[0]

        subprocess.run(["echo hello"])
        subprocess.run(["git checkout origin", branch], stderr=subprocess.PIPE, text=True)
        subprocess.run(["git pull"], stderr=subprocess.PIPE, text=True)
        subprocess.run(["pushd", directory], stderr=subprocess.PIPE, text=True)
        subprocess.run(["docker-compose up"], stderr=subprocess.PIPE, text=True)
        subprocess.run(["popd"], stderr=subprocess.PIPE, text=True)'''

        print(my_commit)
        return my_commit


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
