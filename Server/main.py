#!/usr/bin/python3
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

# -------------------- Globals --------------------

collections_base_path = "./Collections" # Relative path containing the task collections
app = Flask(__name__)
password = "passwd" # API Auth Password
auth = HTTPBasicAuth()
users = { "" : generate_password_hash(password) } # Leave username for blank

# -------------------------------------------------

@app.route('/tasks/<collectionId>', methods=['GET'])
@auth.login_required
def get_tasks(collectionId):
    if os.path.exists("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId)):
        with open(path, 'r') as collection:
            data = json.load(collection)
        return make_response(jsonify(data), 200)
    else:
        return make_response("Collection does not exist.", 404)

@app.route('/tasks/<collectionId>', methods=['POST'])
@auth.login_required
def create_task(collectionId):
    required_params = ['id', 'title', 'completed']
    json_data = request.json

    # Check if the required parameters are sent in the POST request body
    for param in required_params:
        if param not in json_data:
            return make_response("Missing required parameter: '{param}'".format(param=param), 400)
    
    # Check if the task already exists. Return 409 Conflict if it does
    if (os.path.exists("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId))):
        return make_response("Collection already exists.", 409)
    
    # Create the new task collection
    with open("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId), 'w') as file:
        json.dump(json_data, file)
    return make_response("Collection created successfully.", 200)

@app.route('/tasks/<collectionId>', methods=['PUT'])
@auth.login_required
def update_task(collectionId):
    required_params = ['id', 'title', 'completed']
    json_data = request.json
    
    # Check if the required parameters are sent in the POST request body
    for param in required_params:
        if param not in json_data:
            return make_response("Missing required parameter: '{param}'".format(param=param), 400)
    
    # Check if the task exists before updating. Return 404 Not Found if it does not.
    if not (os.path.exists("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId))):
        return make_response("Collection does not exist.", 404)

    # Update the task collection
    with open("{collections_base_path}/{collectionId}".format(collections_base_path=collections_base_path, collectionId=collectionId), 'w') as file:
        json.dump(json_data, file)
    return make_response("Collection updated successfully.", 200)

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

def __main__():
    app.run(host="0.0.0.0", debug=False) 

__main__()