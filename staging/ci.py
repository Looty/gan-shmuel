from os import truncate
from flask import Flask, request
app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    return "good"
@app.route('/health',methods=["GET"])
def health():
    return "ok"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
