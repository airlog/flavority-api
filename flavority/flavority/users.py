
import traceback

from flask.ext.restful import Resource, reqparse
from flask_restful import abort

from . import lm, app
from .models import User
from .util import Flavority

class UserById(Resource):
	"""Handles users with some given id actions
	"""
    def get(self, user_id=None):
		"""Should return user from database in JSON format, 
			if given ID is None should return currently logged in user
		"""
        if user_id is not None:
            return UserById.get_user_by_id(user_id).to_json() 
        else:
            return UserById.get_user_logged().to_json()


    def options(self, user_id=None):
		"""Handles options for requests
		"""
        return None

    @staticmethod
    def get_user_by_id(user_id):
		"""Returns user by given ID or 404 error if there was no user with that ID found in database
		"""
        try:
            return User.query.get(user_id)
        except:
            return abort(404, message="User with id {} doesn't exist".format(user_id))

    @staticmethod
    def get_user_logged():
		"""Returns user if logged in, or 404 if not
		"""
        user = lm.get_current_user()
        if user is None:
            return abort(404, message="User not logged")
        return user
           
