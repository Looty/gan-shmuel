from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/health', methods=['GET'])
def login():
    return render_template('health.html', title='health')
