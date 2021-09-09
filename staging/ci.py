from os import truncate
from flask import Flask, request , json
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
        print(my_commit)
        return my_commit


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
