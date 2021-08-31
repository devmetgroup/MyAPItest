import sqlite3
from flask_restful import Resource, reqparse
from models.user import UserModel

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help='Username cannot be left blank')
    parser.add_argument('password',
        type=str,
        required=True,
        help='Password cannot be left blank')
    
    def post(self):
        request_data = UserRegister.parser.parse_args()
        if UserModel.find_by_username(request_data['username']):
            return {"message": "A user with that username already exists"}, 400
        user = UserModel(**request_data)
        user.save_to_db()
        return {"message": "User created succesfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.json()
    
    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200