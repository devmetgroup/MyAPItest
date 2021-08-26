import sqlite3
from flask_restful import Resource, reqparse

class User:
    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password
    
    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = ?"
        result = cursor.execute(query, (username,))
        row = result.fetchone()
        if row:
            user = cls(*row)
        else:
            user = None
        connection.close()
        return user
    
    @classmethod
    def find_by_id(cls, _id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE id = ?"
        result = cursor.execute(query, (_id,))
        row = result.fetchone()
        if row:
            user = cls(*row)
        else:
            user = None
        connection.close()
        return user

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
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        query = "INSERT INTO users VALUES (NULL, ?, ?)"
        cursor.execute(query, (request_data['username'], request_data['password']))
        connection.commit()
        connection.close()
        return {"message": "User created succesfully."}, 201