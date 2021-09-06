from flask_restful import Resource
from flask import request
from marshmallow import ValidationError
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from models.user import UserModel
from schemas.user import UserSchema
from blacklist import BLACKLIST

NAME_ALREADY_EXISTS = "An user with name '{}' already exists."
ERROR_INSERTING = "An error ocurred while inserting the user."
USER_NOT_FOUND = "User not found."
USER_DELETED = "User deleted."
USER_CREATED = "User created succesfully."
BAD_CREDENTIALS = "Invalid credentials."
SUCESSFULLY_LOGOUT = "User <id={}> Succesfully logged out."

user_schema = UserSchema()

class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            user = user_schema.load(user_json)
        except ValidationError as err:
            return err.messages, 400
        if UserModel.find_by_username(user.username):
            return {"message": NAME_ALREADY_EXISTS.format(user.username)}, 400
        user.save_to_db()
        return {"message": USER_CREATED}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        return user_schema.dump(user)
    
    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {'message': USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json)
        except ValidationError as err:
            return err.messages, 400
        user = UserModel.find_by_username(user_data.username)
        if user and safe_str_cmp(user.password, user_data.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {'message': BAD_CREDENTIALS}, 401

class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()['jti']
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {'message': SUCESSFULLY_LOGOUT.format(user_id)}, 200

class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200