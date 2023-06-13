import os
import json
import logging

import azure.functions as func
from flask import Flask, app, request

app = Flask(__name__)

scriptpath = os.path.abspath(__file__)
ROOT = os.path.dirname(scriptpath)

@app.route("/", methods=['POST', 'GET'])
def home():
    return "I'm Home!"

@app.route("/hello", methods=['POST', 'GET'])
@app.route("/hello/<name>", methods=['GET'])
def article(name:int=None):
    if not name:
        if request.method == 'GET':
            name = request.args.get('name')

        elif request.method == 'POST':
            name = request.form['name']
            if name == '':
                name = None

    if not name:
        with open(os.path.join(ROOT, 'sample.dat')) as fp:
            sample = json.load(fp)
        name = sample['name']

    return 'Hello ' + name

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)
