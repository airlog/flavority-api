from flask.ext.restful import Resource, reqparse
import traceback
from flask_restful import abort
from flavority import lm, app
from .models import Recipe


class Recipes(Resource):

    decorators = [lm.auth_required]

    def get(self):
        recipes = Recipe.query.all()
        app.logger.debug(recipes)
        return [recipe.json for recipe in recipes]

    def post(self):
        args = Recipes.get_form_parser().parse_args()

        recipe = Recipe(args.dish_name, None, args.preparation_time, args.recipe_text, args.portions, lm.get_current_user())
        # TODO: add rest of the arguments

        app.logger.debug(recipe)
        try:
            app.db.session.add(recipe)
            app.db.session.commit()
        except:
            traceback.print_exc()
            app.db.session.rollback()
            return {"result": "failure"}

        return {"result": "success"}, 201

    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('dish_name', type=str, required=True, help="dish name")
        parser.add_argument('recipe_text', type=str, required=True, help="recipe text")
        parser.add_argument('preparation_time', type=int, required=True, help="preparation time")
        parser.add_argument('portions', type=int, required=True, help="portions")

        return parser


class RecipesWithId(Resource):

    decorators = [lm.auth_required]

    def delete(self, recipe_id):

        recipe = RecipesWithId.get_recipe_by_id(recipe_id)

        try:
            app.db.session.delete(recipe)
            app.db.session.commit()
        except:
            app.db.session.rollback()
            return {"result": "failure"}

        return {"result": "success"}

    def put(self, recipe_id):

        recipe = RecipesWithId.get_recipe_by_id(recipe_id)

        args = RecipesWithId.get_form_parser().parse_args()

        RecipesWithId.update_if_set(recipe, args, 'dish_name')
        RecipesWithId.update_if_set(recipe, args, 'recipe_text')
        RecipesWithId.update_if_set(recipe, args, 'preparation_time')
        RecipesWithId.update_if_set(recipe, args, 'portions')
        # TODO: add rest of the arguments

        try:
            app.db.session.commit()
        except:
            app.db.session.rollback()
            return {"result": "failure"}

        return {"result": "success"}

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

        return parser
