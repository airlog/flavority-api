
import traceback

from flask.ext.restful import Resource, reqparse
from flask_restful import abort

from . import lm, app
from .models import User
from .util import Flavority

class UserById(Resource):

    def get(self, user_id):
        return UserById.get_user_by_id(user_id).to_json()

    def options(self):
        return None

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.query.filter(User.id == user_id).one()
        except:
            abort(404, message="User with id {} doesn't exist".format(user_id))

