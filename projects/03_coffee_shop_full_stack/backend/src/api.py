import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
the following line to initialize the datbase
!! THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ROUTES
'''
GET /drinks endpoint
    a public endpoint
    contain only the drink.short() data representation
returns
    status code 200
    json {"success": True, "drinks": drinks} where drinks is list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })


'''
GET /drinks-detail
    it should require the 'get:drinks-detail' permission
    it should contain the drink.long() data representation
returns
    status code 200
    json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })


'''
POST /drinks
    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
returns
    status code 200
    json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    _request = request.get_json()

    try:
        recipe = json.dumps(_request['recipe'])

        drink = Drink(
            title=_request['title'],
            recipe=recipe
        )
        drink.insert()

    except Exception:
        abort(400)

    return jsonify({
        'success': True,
        'drink': drink.long()
    })


'''
PATCH /drinks/<id>
    where <id> is the existing model id
    it responds with a 404 error if <id> is not found
    it updates the corresponding row for <id>
    it requires the 'patch:drinks' permission
    it contains the drink.long() data representation
returns
    status code 200
    json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    _request = request.get_json()

    if 'title' in _request:
        drink.title = _request['title']

    if 'recipe' in _request:
        drink.recipe = json.dumps(_request['recipe'])

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
DELETE /drinks/<id>
    where <id> is the existing model id
    it responds with a 404 error if <id> is not found
    it deletes the corresponding row for <id>
    it requires the 'delete:drinks' permission
returns
    status code 200
    json {"success": True, "delete": id}
    where id is the id of the deleted record
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable():
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
error handler for 404
'''


@app.errorhandler(404)
def not_found():
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
error handler for AuthError
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.error['code'],
        'message': error.error['description']
    }), error.status_code
