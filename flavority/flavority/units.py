
from flask.ext.restful import Resource

from .models import Unit


class UnitResource(Resource):
	"""Unit model class
	"""
    def options(self):
		"""Handles options for requests
		"""
        pass

    def get(self):
		"""Handles GET request
		"""
        query = Unit.query
        return [u.to_json() for u in query.all()]


__all__ = ['UnitResource']
