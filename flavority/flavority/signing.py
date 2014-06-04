
from datetime import datetime
from flask import abort
from flask.ext.restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError

from flavority import app, lm
from .models import User


class Signup(Resource):
    """User sign up model
    """
    @staticmethod
    def get_form_parser():
        """Fetches arguments from parser
        """
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="username")
        parser.add_argument('password', type=str, required=True, help="password")

        return parser            

    @staticmethod
    def get_user(email, password):
        """Returns user from database, error if there was no such user
        """
        user = User.query.filter(User.email == email).first()
        if user is not None:
            raise KeyError()
        
        return User(email, password)

    ###
    ### RESTful
    ###
    def options(self):
        """Handles options for requests
        """
        return None

    def post(self):
        """Handles POST requests
        """
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
    """User sign in model
    """
    @staticmethod
    def get_form_parser():
        """Fetches arguments from parser
        """
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="username")
        parser.add_argument('password', type=str, required=True, help="password")

        return parser            

    ###
    ### RESTful
    ###
    def options(self):
        """Handles options for requests
        """
        return {}, 200
    
    def post(self):
        """Handles POST request
        """
        args = Signin.get_form_parser().parse_args()        
        user = lm.login_user(args["email"], args["password"])
        if user is None:
            abort(403) # invalid username or password
            
        try:
            user.last_seen_date = datetime.now()
            app.db.session.commit()
        except SQLAlchemyError:
            app.db.session.rollback()
                                   
        return {
            "result": "success",
            "token": lm.generate_token(user).decode(),
            'duration': lm.TOKEN_DURATION,
            'user': user.email,
        }

