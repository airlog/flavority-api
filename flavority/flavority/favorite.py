from flask.ext.restful import Resource, reqparse
from flask_restful import abort
from sqlalchemy.exc import SQLAlchemyError

from . import lm, app
from .models import Recipe, User
from .util import Flavority

from .util import Flavority, ViewPager


class FavoriteRecipes(Resource):

    GET_ITEMS_PER_PAGE = 10

    @staticmethod
    def parse_get_arguments():
        def cast_natural(x):
            try: i = int(x)
            except ValueError: return 1
            return i if i >= 1 else 1
            
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=cast_natural, default=1)
        parser.add_argument('limit', type=cast_natural, default=FavoriteRecipes.GET_ITEMS_PER_PAGE)
        return parser.parse_args()

    @staticmethod
    def parse_post_arguments():
        def cast_natural(x):
            try: i = int(x)
            except ValueError: return 1
            return i if i >= 1 else 1
            
        parser = reqparse.RequestParser()
        parser.add_argument('recipe_id', type=cast_natural, default=0)
        return parser.parse_args()

    def options(self, recipe_id =None):
        return None

    @lm.auth_required
    def get(self):
        args = self.parse_get_arguments()
        user = lm.get_current_user()
        query = user.favourites
        total_elements = query.count()
        func = lambda x: x.to_json_short(get_photo=lambda photo: photo.id)
        query = ViewPager(query, page=args['page'], limit_per_page=args['limit'])
        return {
            'recipes': list(map(func, query.all())),
            'totalElements': total_elements,
        }

    @lm.auth_required
    def post(self, recipe_id = None):
        args = self.parse_post_arguments()
        user = lm.get_current_user()
        recipe = Recipe.query.get(args['recipe_id'])
        try:
            if recipe is not None and recipe not in user.favourites:
                user.favourites.append(recipe)
            app.db.session.commit()
        except SQLAlchemyError as e:
            app.logger.error(e)
            app.db.session.rollback()
            return abort(500)
        return Flavority.success()

    @lm.auth_required
    def delete(self, recipe_id = None):
        user = lm.get_current_user()
        recipe = user.favourites.filter(Recipe.id == recipe_id).first()
        try:
            if recipe is not None:
                user.favourites.remove(recipe)
                app.db.session.commit()
        except SQLAlchemyError as e:
            app.logger.error(e)
            app.db.session.rollback()
            return abort(500)
        return Flavority.success()

