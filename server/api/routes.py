from api import jsonify, request, url_for,  Resource, User, SQLAlchemyError, make_response,  \
     send_from_directory,  Migrate, db, Api,  \
   Namespace, Marshmallow, fields, check_password_hash, datetime, uuid
from api import app, ma, api
from .api_models import *
from .models import Category, Transaction, User, Photo, Cart, CartItem
import os
from functools import wraps
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required


ns = Namespace('snapstore')
api.add_namespace(ns)


@ns.route('/signup')
class Signup(Resource):
    @ns.expect(user_input_schema)
    @ns.marshal_with(user_schema)
    def post(self):
        data = request.get_json()
        # print("signup",data)
        if data['password'] == data['repeatPassword']:
            if data:
                new_user = User(
                    username=data['username'],
                    email=data['email'],
                    public_id=str(uuid.uuid4())
                )
                new_user.set_password(data['password'])
                print(f'new user:{new_user}')
                new_user.set_password(data['password'])
                db.session.add(new_user)
                db.session.commit()
                print("new added user",new_user)
                return new_user, 201
            else:
                return {'message': "No data found"}, 404
        else:
            return {'message': "No data found"}, 404
