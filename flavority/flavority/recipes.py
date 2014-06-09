
import traceback
from base64 import b64decode
from functools import reduce
from json import loads as json_loads
from os.path import abspath, join

from flask import request
from flask.ext.restful import Resource, reqparse, abort
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from . import lm, app
from .models import Recipe, Tag, tag_assignment, Ingredient, IngredientUnit, IngredientAssociation, Photo, Unit, User
from .util import Flavority, ViewPager
from .photos import PhotoResource


class Recipes(Resource):

    GET_ITEMS_PER_PAGE = 10

    @staticmethod
    def parse_get_arguments():
        def cast_bool(x):
            if x.lower() == '': return True
            elif x.lower() == 'false': return False
            elif x.lower() == 'true': return True
            try:
                return bool(x)
            except ValueError:
                return False

        def cast_sort(x):
            sortables, x = ['id', 'date_added', 'rate'], x.lower()
            return x if x in sortables else sortables[0]

        def cast_natural(x):
            try: i = int(x)
            except ValueError: return 1
            return i if i >= 1 else 1

        parser = reqparse.RequestParser()
        parser.add_argument('short', type=cast_bool)
        parser.add_argument('sort_by', type=cast_sort, default='id')
        parser.add_argument('page', type=cast_natural, default=1)
        parser.add_argument('limit', type=cast_natural, default=Recipes.GET_ITEMS_PER_PAGE)
        parser.add_argument('user_id', type=int, default=None)
        parser.add_argument('query', type=str)
        parser.add_argument('tag_id', type=int, default=None, action='append')
        parser.add_argument('advanced', type=cast_bool, default=False)
        parser.add_argument('myrecipes', type=cast_bool, default=False)
        return parser.parse_args()

    @staticmethod
    def parse_post_arguments():
        def cast_difficulty(val):
            f = float(val)
            if f in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
                return f
            raise ValueError('can not cast \'{}\' to difficulty'.format(val))

        def cast_ingredients(val):
            res = []
            for ele in val:
                ingr_id, amount, unit = ele[0], ele[1], ele[2]
                res.append((ingr_id, amount, unit))
            return res

        parser = reqparse.RequestParser()
        parser.add_argument('dish_name', type=str, required=True, help="dish name")
        parser.add_argument('recipe_text', type=str, required=True, help="recipe text")
        parser.add_argument('preparation_time', type=int, required=True, help="preparation time in minutes")
        parser.add_argument('portions', type=int, required=True, help="portions info is missing")
        parser.add_argument('difficulty', type=cast_difficulty, required=True, help='difficulty is missing')
        parser.add_argument('ingredients', type=cast_ingredients, required=True, help="ingredients are missing")
        parser.add_argument('tags', type=list, default=[])
        parser.add_argument('photos', type=list, default=[])
        parser.add_argument('remove_photos', type=list, default=[])

        return parser.parse_args()

    def options(self):
        return None

    def get(self):
        args = self.parse_get_arguments()

        query = Recipe.query

        if args['advanced']:
#          funkcja do napisania dla Patryka
#           w query znajduje sie lista skladnikow
           return #advancedSearch(args['query'], args['page'], args['limit'])

        # only recipes containg at least one of the requested tags
        #   this piece of code may require an explanation:
        #       the idea is to take all recipes marked with a given tag (one) and union results
        #       in order to avoid None objects they're filtered out
        if args.tag_id is not None:
            query = reduce(
                lambda q1, q2: q1.union(q2),
                map(
                    lambda tag: tag.recipes,
                    filter(lambda x: x is not None, [Tag.query.get(i) for i in args.tag_id])))

        # only recipes from given user
        if args['user_id']:
            query = query.filter(Recipe.author_id == args['user_id'])
        elif args['myrecipes']:
            user = lm.get_current_user()
            query = user.recipes
        
        # search string in titles
        if args['query'] is not None:
            pattern = args['query'].lower()
            query = query.filter(Recipe.dish_name.like('%{}%'.format(pattern)))

        # select proper sorting key
        query = {
            'id': lambda x: x,
            'date_added': lambda x: x.order_by(Recipe.creation_date.desc()),
            'rate': lambda x: x.order_by(Recipe.taste_comments.desc())
        }[args['sort_by']](query)
        total_elements = query.count()
        query = ViewPager(query, page=args['page'], limit_per_page=args['limit'])

        # return short or standard form as requested
        func = lambda x: x.to_json()
        if args['short']:
            func = lambda x: x.to_json_short(get_photo=lambda photo: photo.id)

        return {
            'recipes': list(map(func, query.all())),
            'totalElements': total_elements,
        }

    @lm.auth_required
    def post(self):
        """
        Attempts creation of a new Recipe object in the database. Parameters required by this method are listed
        in :func:`Recipe.parse_post_arguments`.

        This method will return a HTTP201 with a ID of just created recipe. Should any error occur the proper HTTP
        errors will be throw.
        """

        def add_tags(rcp, tags_names):
            tags = []
            for name in tags_names:
                try:
                    tid = int(name)
                    tag = Tag.query.get(tid)
                    if tag is None: raise ValueError()
                except ValueError:
                    tag = Tag\
                        .query\
                        .filter(func.lower(Tag.name) == name.lower())\
                        .first()
                tags.append(tag if tag is not None else Tag(name))
            rcp.tags = tags

        def add_ingredients(rcp, ingrs):
            ingredients = []
            for ingr_name, amount, unit_name in ingrs:
                ingr, unit = Ingredient.query.filter(Ingredient.name == ingr_name).first(),\
                             Unit.query.filter(Unit.unit_name == unit_name).first()
                if ingr is None:
                    ingr = Ingredient(ingr_name)
                if unit is None:
                    unit = Unit(unit_name, None, None)
                iu = IngredientUnit\
                    .query\
                    .filter(IngredientUnit.ingredient_id == ingr.id, IngredientUnit.unit_id == unit.id)\
                    .first()
                if iu is None:
                    iu = IngredientUnit(ingr, unit)

                ia = IngredientAssociation(iu, amount)
                ingredients.append(ia)
            rcp.ingredients = ingredients

        def add_photos(rcp, photo_ids):
            for photo in filter(lambda x: x is not None, (Photo.query.get(id) for id in photo_ids)):
                # photos must not be already attached to any recipe
                if photo.is_attached(): return abort(403)
                rcp.photos.append(photo)

        def remove_unused_photos(photo_ids):
            if photo_ids is None: return
            for pid in photo_ids:
                photo = Photo.query.get(pid)
                if photo is None: continue
                if not photo.is_attached():
                    app.db.session.delete()

        args, user = self.parse_post_arguments(), lm.get_current_user()

        recipe = Recipe(
            args.dish_name,
            args.preparation_time,
            args.recipe_text,
            args.portions,
            args.difficulty,
            user.id)
        add_tags(recipe, args.tags)
        add_ingredients(recipe, args.ingredients)
        add_photos(recipe, args.photos)
        remove_unused_photos(args.remove_photos)

        try:
            app.db.session.add(recipe)
            app.db.session.commit()
        except SQLAlchemyError as e:
            app.logger.error(e)
            app.db.session.rollback()
            return Flavority.failure(), 500

        return {'id': recipe.id}, 201


class RecipesWithId(Resource):

    @staticmethod
    def get_recipe_by_id(recipe_id):
        try:
            return Recipe.query.filter(Recipe.id == recipe_id).one()
        except:
            abort(404, message="Recipe with id {} doesn't exist".format(recipe_id))

    @staticmethod
    def update_if_set(recipe, args, field):
        field_value = getattr(args, field)
        if field_value is not None:
            setattr(recipe, field, field_value)

    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('dish_name', type=str, help="dish name")
        parser.add_argument('recipe_text', type=str, help="recipe text")
        parser.add_argument('preparation_time', type=int, help="preparation time")
        parser.add_argument('portions', type=int, help="portions")
        parser.add_argument('tags', type=int, help="tags", action="append")
        parser.add_argument('ingredients', type=list, help="ingredients")

        return parser

    @staticmethod
    def get_recipe_with_tags(tag_list):
        if len(tag_list) > 0:
            try:
                return Recipe.query.join(tag_assignment).filter(tag_assignment.tag.in_(tag_list)).all()
            except:
                abort(404, message="No recipes with given tags!")
        else:
            return -1   # Error

    def options(self, recipe_id=None):
        return None

    def get(self, recipe_id):
        my_recipe = False
        favorite = False
        recipe = RecipesWithId.get_recipe_by_id(recipe_id)
        user = lm.get_current_user()
        if user is not None:
            if recipe.author_id == user.id:
                my_recipe = True
            if recipe in user.favourites:
                favorite = True
        return {
            'recipe': recipe.to_json(),
            'favorite': favorite,
            'my_recipe': my_recipe, 
        }

    @lm.auth_required
    def delete(self, recipe_id):
        user = lm.get_current_user()
        recipe = user.recipes.filter(Recipe.id == recipe_id).first()
        try:
            tags_to_remove = filter(lambda tag: tag.recipes.count() == 1, recipe.tags)
            for tag in tags_to_remove:
                app.db.session.delete(tag)
            for photo in recipe.photos:
                app.db.session.delete(photo)                        
            app.db.session.delete(recipe)
            app.db.session.commit()
        except:
            app.db.session.rollback()
            return Flavority.failure()

        return Flavority.success()

    @lm.auth_required
    def put(self, recipe_id):

        recipe = RecipesWithId.get_recipe_by_id(recipe_id)

        args = RecipesWithId.get_form_parser().parse_args()

        RecipesWithId.update_if_set(recipe, args, 'dish_name')
        RecipesWithId.update_if_set(recipe, args, 'recipe_text')
        RecipesWithId.update_if_set(recipe, args, 'preparation_time')
        RecipesWithId.update_if_set(recipe, args, 'portions')
        Recipes.add_tags(recipe, args.tags)
        Recipes.add_ingredients(recipe, args.ingredients)

        # TODO: add rest of the arguments

        try:
            app.db.session.commit()
        except:
            traceback.print_exc()
            app.db.session.rollback()
            return Flavority.failure(), 500

        return Flavority.success()


__all__ = ['Recipes', 'RecipesWithId']
