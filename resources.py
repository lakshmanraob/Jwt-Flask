from flask_restful import Resource, reqparse

from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt, decode_token)
import datetime

parser = reqparse.RequestParser()
parser.add_argument('username', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)

client = MongoClient('localhost:27017')
db = client.myDatabase

ACCESS_EXPIRE = datetime.timedelta(minutes=5)
REFRESH_EXPIRE = datetime.timedelta(days=1)


class SampleResponse(Resource):
    def get(self):
        return {'message': 'jwt-flask'}


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()

        is_username_exists = db.user.find({'username': data['username']})

        if is_username_exists.count() > 0:
            return {'message': 'you are already registered'}, 500
        else:
            user = {
                'username': data['username'],
                'hash': sha256.hash(data['password'])
            }
            user_id = db.user.insert_one(user).inserted_id
            return {'message': 'user {} is created and the id is {}'.format(data['username'], user_id)}


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()

        user_in_db = db.user.find_one({'username': data['username']})
        print(data['password'])
        print(user_in_db)

        if user_in_db:
            if self.verify_hash(data['password'], user_in_db['hash']):
                # token_cursor = db.tokens.find({'username': data['username'], 'isActive': True})
                # if token_cursor.count() > 0:
                #     print(decode_token(token_cursor[0]['access_token'])['exp'])
                #     if decode_token(token_cursor[0]['access_token'])['exp'] < datetime.datetime.utcnow():
                #         my_query = {'_id': token_cursor[0]['_id']}
                #         new_values = {"$set": {'isActive': False}}
                #         db.tokens.update_one(my_query, new_values)
                #         print("access token expired")
                #         # print(decode_token(token_cursor[0]['refresh_token'])['exp'])
                # else:
                access_token = create_access_token(identity=data['username'], expires_delta=ACCESS_EXPIRE)
                refresh_token = create_refresh_token(identity=data['username'], expires_delta=REFRESH_EXPIRE)
                print(decode_token(access_token))
                print(decode_token(refresh_token))

                return {'message': 'you are logged in as {}'.format(data['username']),
                        'access_token': access_token,
                        'refresh_token': refresh_token}
            else:
                return {'message': 'password mismatch'}, 400
        else:
            return {'message': 'no user present with username as {}'.format(data['username'])}

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        print(jti)
        # adding the access token jti to the token class
        token = {
            "access_token_jti": jti
        }
        inserted_id = db.tokens.insert_one(token).inserted_id
        return {'message': 'logout successful'}


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        print(jti)
        # adding the refresh token jti to the token class
        token = {
            "refresh_token_jti": jti
        }
        inserted_id = db.tokens.insert_one(token).inserted_id
        return {'message': 'logout successful'}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        all_users = list(db.user.find({}, {'_id': False}))
        # print(all_users)
        return {'users': all_users}

    def delete(self):
        results = db.user.delete_many({})
        return {'message': 'successfully deleted {}'.format(results.deleted_count)}


class SecretResource(Resource):
    @jwt_required
    def get(self):
        jti = get_raw_jwt()['jti']
        jti_tokens = db.tokens.find({'access_token_jti': jti})
        if jti_tokens.count() > 0:
            return {'message': 'token expired'}, 400
        else:
            return {'answer': 42}
