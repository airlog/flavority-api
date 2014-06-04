
from flask.ext.restful import Resource

from .models import Unit


class UnitResource(Resource):

    def options(self):
        pass

    def get(self):
        query = Unit.query
        return [u.to_json() for u in query.all()]


__all__ = ['UnitResource']
