
from flask import abort
from flask.ext.restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError

from flavority import app, lm
from .models import User


class Signup(Resource):
    
    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="username")
        parser.add_argument('password', type=str, required=True, help="password")

        return parser            

    @staticmethod
    def get_user(email, password):
        user = User.query.filter(User.email == email).first()
        if user is not None:
            raise KeyError()
        
        return User(email, password)

    ###
    ### RESTful
    ###
    def options(self):
        return None

    def post(self):
        args = Signup.get_form_parser().parse_args()        
        try:
            user = self.get_user(args.email, args.password)
        except KeyError:
            abort(403)  # email already in the database
        
        try:
            app.db.session.add(user)
            app.db.session.commit()
        except SQLAlchemyError:
            app.db.session.rollback()
        
        return {
            "result": "success",
            "email": user.email,
        }, 204


class Signin(Resource):
        
    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="username")
        parser.add_argument('password', type=str, required=True, help="password")

        return parser            

    ###
    ### RESTful
    ###
    def options(self):
        return {}, 200
    
    def post(self):
        args = Signin.get_form_parser().parse_args()        
        user = lm.login_user(args["email"], args["password"])
        if user is None:
            abort(403) # invalid username or password

        return {
            "result": "success",
            "token": lm.generate_token(user).decode(),
            'duration': lm.TOKEN_DURATION,
            'user': user.email,
        }

