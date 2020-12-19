from http import HTTPStatus
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required, get_raw_jwt
from utils import check_password
from models.user import User

blacklist = set()

class TokenResource(Resource):

    def post(self):
        json_data = request.get_json()
        email = json_data.get('email')
        password = json_data.get('password')

        user = User.get_by_email(email)
        if not user or not check_password(password, user.password):
            return {'message':'email or password is incorrect'}, HTTPStatus.UNAUTHORIZED
        if user.is_active is False:
            return {'message':'User account must be activated'}, HTTPStatus.FORBIDDEN
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        return {'access_token':access_token,'refresh_token':refresh_token}, HTTPStatus.OK

class RefreshResource(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token':access_token}, HTTPStatus.OK


class RevokeResource(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)

        return {'message':'Successfully logged out'}, HTTPStatus.OK
