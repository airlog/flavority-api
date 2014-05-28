
from flask.ext.restful import Resource, reqparse
from sqlalchemy import desc, func

from . import app
from .models import Ingredient
from .util import ViewPager


class IngredientsResource(Resource):

    GET_ITEMS_PER_PAGE = 30

    def options(self):
        return None

    def get(self):
        """
        Returns a list of all ingredients in database ordered by name.
        """
        return [{'id': ingr.id, 'name': ingr.name} for ingr in Ingredient.query.order_by(func.lower(Ingredient.name)).all()]

