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