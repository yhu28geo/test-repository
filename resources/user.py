import sqlite3
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
    )
from models.user import UserModel
from blacklist import BLACKLIST

# "_" indicate that the variables are private, which should not be imported from elsewhere 
_user_parser = reqparse.RequestParser() 
_user_parser.add_argument('username',
                           type=str,
                           required=True,
                           help="This field cannot be left blank!"
                         ) 
_user_parser.add_argument('password',
                           type=str,
                           required=True,
                           help="This field cannot be left blank!"
                         )

class UserRegister(Resource):
    
    def post(self):
        data = _user_parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return {"message": "A user with username already exist"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201

class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message':'User not found'}, 404
        return user.json()
    
    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message':"User not found"}, 404
        user.delete_from_db()
        return {'message':'User deleted.'}, 200

class UserLogin(Resource):
    @classmethod
    def post(cls):
        #get data from parser
        data = _user_parser.parse_args()

        #find user in database
        user = UserModel.find_by_username(data['username'])

        #This is what the 'authenticate()' function to do
        if user and safe_str_cmp(user.password, data['password']):
            # 'identity=' is what the 'identity()' function used to do
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        
        return {'message': 'Invalid credentials'}, 401

class UserLogout(Resource):
    @jwt_required
    #perform logout by blacklisting specific token (via token's id)
    def post(self):
        jti = get_raw_jwt()['jti']  # jti is "JWT ID", is a unique identifier for JWT
        BLACKLIST.add(jti)
        return {'message':'Successfully logged out.'}

#create refresh token
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200

#return them