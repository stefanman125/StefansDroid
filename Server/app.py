#!/usr/bin/python3
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import re

# -------------------- Globals --------------------

collections_base_path = os.path.abspath(os.path.join(str(__file__), os.pardir))+"/Collections" # Absolute path containing the task collections
app = Flask(__name__)
app.json.sort_keys = False
password = "assface" # API Auth Password
auth = HTTPBasicAuth()
users = { "" : generate_password_hash(password) } # Leave username for blank

# -------------------------------------------------

@app.route('/tasks/<collectionId>', methods=['GET'])
@auth.login_required
def get_collection(collectionId):
    collection_exists = os.path.exists("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId))

    if collection_exists:
        with open("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId), 'r') as collection:
            data = json.load(collection)
        return make_response(jsonify(data), 200)
    else:
        return make_response("Collection does not exist.", 404)

@app.route('/tasks/<collectionId>', methods=['POST', 'PUT'])
@auth.login_required
def manage_collections(collectionId):
    # Required parameters and value types
    required_params = {'lastModified': int, 'tasks': list} # Only required for creating empty collections
    required_task_params = {'id': int, 'title': str, 'completed': bool} # Only required for tasks within the task list of a collection
    json_data = request.json

    # Check if the required parameters are sent in the POST request body, and if they follow the expected variable type
    for param, expected_type in required_params.items():
        if param not in json_data:
            return make_response("Missing required parameter: {param}".format(param=param), 400)
        elif not isinstance(json_data[param], expected_type):
            return make_response("Parameter {param} must be a '{type}' type.".format(param=param, type=expected_type.__name__), 400)
    
    # Check if the required parameters are sent in each task body, and if they follow the expected value
    for param, expected_type in required_task_params.items():
        for task in json_data['tasks']:
            if param not in task:
                return make_response("Missing required task parameter: {param}".format(param=param), 400)
            elif not isinstance(task[param], expected_type):
                return make_response("Task Parameter {param} must be a '{type}' type.".format(param=param, type=expected_type.__name__), 400)
    
    # Check if the task collection already exists
    collection_exists = os.path.exists("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId))

    # If the collection exists and the user is trying to create it, return a 409
    if (collection_exists and request.method == "POST"):
        return make_response("Collection already exists.", 409)

    # If the collection does not exist and the user is trying to update it, return a 404
    elif (not collection_exists and request.method == "PUT"):
        return make_response("Collection does not exist.", 404)
    
    if (request.method == "POST"):
        # Create the new task collection
        with open("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId), 'w') as file:
            json.dump(json_data, file)
        return make_response("Collection created successfully.", 200)
    
    elif (request.method == "PUT"):
        # Update the task collection
        with open("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId), 'w') as file:
            json.dump(json_data, file)
        return make_response("Collection updated successfully.", 200)
    
@app.route('/tasks/<collectionId>', methods=['DELETE'])
@auth.login_required
def delete_collection(collectionId):
    # Check if the task collection exists
    collection_exists = os.path.exists("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId))

    # If the collection does not exist and the user is trying to delete it, return a 404
    if (not collection_exists and request.method == "DELETE"):
        return make_response("Collection does not exist.", 404)
    else:
        os.remove("{collections_base_path}/{collectionId}.json".format(collections_base_path=collections_base_path, collectionId=collectionId))
        return make_response("Collection successfully deleted.", 200)

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

def __main__():
    # Uncomment this to run in a development environment
    app.run(host="0.0.0.0", debug=False) 
    pass

__main__()
