from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blacklist import BLACKLIST

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = 'jose'
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()
    
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_data):
    return jwt_data['jti'] in BLACKLIST

api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)