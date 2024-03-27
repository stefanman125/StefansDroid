#!/usr/bin/python3
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

# -------------------- Globals --------------------

app = Flask(__name__)
password = "passwd" # API Auth Password
auth = HTTPBasicAuth()
users = { "" : generate_password_hash(password) } # Leave username for blank

# -------------------------------------------------

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route('/tasks/<collectionId>', methods=['GET'])
@auth.login_required
def get_tasks(collectionId):
    # If the collection exists, return its contents. If not, return a 404
    path = "./Collections/{collectionId}.json".format(collectionId=collectionId)
    if os.path.exists(path):
        with open(path, 'r') as collection:
            data = json.load(collection)
        return make_response(jsonify(data), 200)
    else:
        return make_response("Collection does not exist.", 404)

def __main__():
    app.run(host="0.0.0.0", debug=False) 

__main__()