import traceback
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
EMAIL_ALREADY_EXISTS = "An user with email '{}' already exists."
ERROR_INSERTING = "An error ocurred while inserting the user."
USER_NOT_FOUND = "User not found."
USER_DELETED = "User deleted."
USER_CREATED = "User created succesfully, an email with an activation link has been sent to your email address, please check."
BAD_CREDENTIALS = "Invalid credentials."
SUCESSFULLY_LOGOUT = "User <id={}> Succesfully logged out."
NOT_CONFIRMED_ERROR = "You have not confirmed registration, please check your email <{}>"
USER_CONFIRMED = "User confirmed."
FAILED_TO_CREATE = "Internal server error, failed to create user."

user_schema = UserSchema()

class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)
        if UserModel.find_by_username(user.username):
            return {"message": NAME_ALREADY_EXISTS.format(user.username)}, 400
        if UserModel.find_by_email(user.email):
            return {"message": EMAIL_ALREADY_EXISTS.format(user.email)}, 400
        try:
            user.save_to_db()
            user.send_confirmation_email()
            return {"message": USER_CREATED}, 201
        except:
            traceback.print_exc()
            return {"message": FAILED_TO_CREATE}, 500


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
        user_json = request.get_json()
        user_data = user_schema.load(user_json, partial=("email",))
        user = UserModel.find_by_username(user_data.username)
        if user and safe_str_cmp(user.password, user_data.password):
            if user.activated:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, 200
            return {"message": NOT_CONFIRMED_ERROR.format(user.username)}, 400
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
    
class UserConfirm(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.activated = True
        user.save_to_db()
        return {"message": USER_CONFIRMED}, 200