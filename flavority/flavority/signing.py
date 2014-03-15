
from binascii import hexlify
from os import urandom

from flask.ext.restful import Resource, reqparse

from flavority import app, lm
from .models import User

class Signup(Resource):
    
    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('email', type = str, required = True, help = "username")
        parser.add_argument('password', type = str, required = True, help = "password")

        return parser            

    def get_user(self, email, password):
        user = User.query.filter(User.email == email).first()
        if user is not None: raise KeyError()
        
        return User(email, password)

    ###
    ### RESTful
    ###
    def post(self):
        args = Signup.get_form_parser().parse_args()        
        try:
            user = self.get_user(args.email, args.password)
        except KeyError:
            return {
                    "result": "fail",
                    "error": "given email already in the database",
                }
        
        try:
            app.db.session.add(user)
            app.db.session.commit()
        except:
            app.db.session.rollback()
        
        return {
                "result": "success",
            }
        
class Signin(Resource):
        
    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('email', type = str, required = True, help = "username")
        parser.add_argument('password', type = str, required = True, help = "password")

        return parser            

    ###
    ### RESTful
    ###
    def post(self):
        args = Signin.get_form_parser().parse_args()        
        user = lm.login_user(args["email"], args["password"])
        if user is None: return {
                "result": "fail",
                "error": "invalid username or password",
            }
        
        try:
            return {
                    "result": "success",
                    "token": lm.register_user(user),
                }
        except ValueError:
            # user already signed in
            return {
                    "result": "fail",
                    "error": "user already signed in",
                }

class Signout(Resource):
    
    decorators = [lm.auth_required]
    
    def signout_user(self):
        try:
            lm.unregister_user()
            return {
                    "result": "success",
                }
        except KeyError:
            # user already signed in
            return {
                    "result": "fail",
                    "error": "user not signed in",
                }
             
    ###
    ### RESTful
    ###
    def get(self):
        return self.signout_user()
    
    def post(self):
        return self.signout_user()

