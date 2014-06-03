
from flask.ext.restful import Resource, reqparse
from sqlalchemy import desc, func

from . import app
from .models import Ingredient
from .util import ViewPager


##Class that handles ingredient control
class IngredientsResource(Resource):

    ##Variable that represents total ingredient number that can be visible at page
    GET_ITEMS_PER_PAGE = 30

    ##Handles options for HTTP request
    def options(self):
        return None

    ##Returns a list of all ingredients in database ordered by name.
    def get(self):
        """
        Returns a list of all ingredients in database ordered by name.
        """
        return [{'id': ingr.id, 'name': ingr.name} for ingr in Ingredient.query.order_by(func.lower(Ingredient.name)).all()]

