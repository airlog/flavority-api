
import traceback

from flask.ext.restful import Resource, reqparse
from flask_restful import abort

from . import lm, app
from .models import User
from .util import Flavority


##Class handles User actions
class UserById(Resource):

    ##Method handles GET request
    def get(self, user_id=None):
        if user_id is not None:
            return UserById.get_user_by_id(user_id).to_json() 
        else:
            return UserById.get_user_logged().to_json()

    ##Method handles options for requests
    def options(self, user_id=None):
        return None

    ##Method should return user with given ID
    #May return 404 error if there is no user with given ID in database.
    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.query.get(user_id)
        except:
            return abort(404, message="User with id {} doesn't exist".format(user_id))

    ##Method should return currently logged in user
    #May return 404 error if user is not logged.
    @staticmethod
    def get_user_logged():
        user = lm.get_current_user()
        if user is None:
            return abort(404, message="User not logged")
        return user