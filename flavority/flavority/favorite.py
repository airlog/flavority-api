import traceback

from flask.ext.restful import Resource, reqparse
from flask_restful import abort

from . import lm, app
from .models import Recipe, User
from .util import Flavority

from .util import Flavority, ViewPager


class FavoriteRecipes(Resource):

    GET_ITEMS_PER_PAGE = 10

    def options(self, recipe_id =None):
        return None


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
        try:
            user = lm.get_current_user()
            user = User.query.first()
            recipe = Recipe.query.get(recipe_id)
            if recipe is not None and recipe not in user.favourites:
                user.favourites.append(recipe)
                app.db.session.commit()
        except:
            app.db.session.rollback()
            return Flavority.failure(), 500

        return Flavority.success()


    @lm.auth_required
    def delete(self, recipe_id = None):
        try:
            user = User.query.first()
            user = lm.get_current_user()
            recipe = user.favourites.filter(Recipe.id == recipe_id).first()
            if recipe is not None:
                user.favourites.remove(recipe)
                app.db.session.commit()
        except:
            app.db.session.rollback()
            return Flavority.failure()

        return Flavority.success()

