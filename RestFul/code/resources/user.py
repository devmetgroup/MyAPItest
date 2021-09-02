from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
from models.user import UserModel
from blacklist import BLACKLIST

BLANK_ERROR = "'{}' cannot be blank!"
NAME_ALREADY_EXISTS = "An user with name '{}' already exists."
ERROR_INSERTING = "An error ocurred while inserting the user."
USER_NOT_FOUND = "User not found."
USER_DELETED = "User deleted."
USER_CREATED = "User created succesfully."
BAD_CREDENTIALS = "Invalid credentials."
SUCESSFULLY_LOGOUT = "User <id={user_id}> Succesfully logged out."

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                        type=str,
                        required=True,
                        help=BLANK_ERROR.format('username')
                        )
_user_parser.add_argument('password',
                        type=str,
                        required=True,
                        help=BLANK_ERROR.format('password')
                        )

class UserRegister(Resource):
    @classmethod
    def post(cls):
        request_data = _user_parser.parse_args()
        if UserModel.find_by_username(request_data['username']):
            return {"message": NAME_ALREADY_EXISTS.format(request_data['username'])}, 400
        user = UserModel(**request_data)
        user.save_to_db()
        return {"message": USER_CREATED}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        return user.json()
    
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
        request_data = _user_parser.parse_args()
        user = UserModel.find_by_username(request_data['username'])
        if user and safe_str_cmp(user.password, request_data['password']):
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