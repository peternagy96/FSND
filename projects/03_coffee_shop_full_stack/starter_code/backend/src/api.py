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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    drinks_short_form = []
    for drink in drinks:
        drink = drink.long()
        drinks_short_form.append(drink)
    
    return jsonify({
        "success": True, 
        "drinks": drinks_short_form
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def show_drinks_detail(jwt):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            'success':True,
            'drinks':drinks
        })
    except:
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(token):
    try:
        req = request.get_json()
        new_title = req.get('title', None)
        new_recipe = json.dumps(req.get('recipe', None))
        new_drink = Drink(
        title = new_title,
        recipe = new_recipe
        )
        print(new_title)
        if Drink.query.filter(Drink.title == new_title).one_or_none():
            abort(409)
        new_drink.insert()
        return jsonify({
            'success':True,
            'drinks': [new_drink.long()]
        })
    except:
        abort(404)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth(permission='patch:drinks')
def patch_drinks_details(token, drink_id):
    try:
        req = request.get_json()
        title = req.get('title', None)
        recipe = json.dumps(req.get('recipe', None))

        if not title or not recipe:
            abort(422)

        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        
        if not drink:
            abort(400)

        drink.title = title
        drink.recipe = recipe
        drink.update()

        return jsonify({
            "success": True, 
            "drinks": drink.long()
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drinks(token, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        
        if not drink:
            abort(400)

        drink.delete()

        return jsonify({
            "success": True, 
            "delete": drink_id
        })
    except:
        abort(422)


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "unprocessable"
                    }), 401