
from flask import request

from flask.ext.restful import Resource, reqparse
import traceback
from flask_restful import abort
from flavority import lm, app

from .models import Recipe, Tag, tag_assignment, Ingredient, IngredientAssociation
from .util import Flavority


class Recipes(Resource):

    def get(self):
        short = request.args.get('short', None)
        # handling ?short
        if short is not None:
            return Flavority.success(**{
                     'recipes-short': list(map(lambda x: x.to_json_short(), Recipe.query.all())),
                })

        app.logger.debug('short = {}'.format(short))
        recipes = Recipe.query.all()
        app.logger.debug(recipes[0].ingredients)
        return Flavority.success(recipes=[recipe.json for recipe in recipes])

    @lm.auth_required
    def post(self):
        args = Recipes.get_form_parser().parse_args()

        recipe = Recipe(args.dish_name, None, args.preparation_time, args.recipe_text, args.portions, lm.get_current_user())
        Recipes.add_tags(recipe, args.tags)
        Recipes.add_ingredients(recipe, args.ingredients)

        # TODO: add rest of the arguments

        app.logger.debug(recipe)
        try:
            app.db.session.add(recipe)
            app.db.session.commit()
        except:
            traceback.print_exc()
            app.db.session.rollback()
            return Flavority.failure(), 500

        return Flavority.success(), 201

    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('dish_name', type=str, required=True, help="dish name")
        parser.add_argument('recipe_text', type=str, required=True, help="recipe text")
        parser.add_argument('preparation_time', type=int, required=True, help="preparation time")
        parser.add_argument('portions', type=int, required=True, help="portions")
        parser.add_argument('tags', type=list, required=False, help="tags", action="append")
        parser.add_argument('ingredients', type=list, required=True, help="ingredients")

        return parser

    @staticmethod
    def add_ingredients(recipe, ingredients):
        if ingredients is not None:
            ingredient_id_to_amount = {association["ingr_id"]: association["amount"] for association in ingredients}
            available_ingredients = \
                Ingredient.query.filter(Ingredient.id.in_(','.join([str(assoc["ingr_id"]) for assoc in ingredients]))).all()

            if len(ingredient_id_to_amount) != len(available_ingredients):
                abort(500, message="Not all ingredients are present in the database")

            recipe.ingredients = []

            for ingr in available_ingredients:
                assoc = IngredientAssociation()
                assoc.ingredient = ingr
                assoc.amount = ingredient_id_to_amount[ingr.id]
                recipe.ingredients.append(assoc)

    @staticmethod
    def add_tags(recipe, tags):
        if tags is not None:
            recipe.tags = Tag.query.filter(Tag.id.in_(','.join([str(i) for i in tags]))).all()


class RecipesWithId(Resource):

    decorators = [lm.auth_required]

    def delete(self, recipe_id):

        recipe = RecipesWithId.get_recipe_by_id(recipe_id)

        try:
            app.db.session.delete(recipe)
            app.db.session.commit()
        except:
            app.db.session.rollback()
            return Flavority.failure()

        return Flavority.success()

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
            return -1       #Error!

    # @staticmethod
    # def get_recipe_with_ingredients(ingredient_list):
    #     if len(ingredient_list) > 0:
    #         try:
    #             return Recipe.query.join(ingredient_assignment).filter(ingredient_assignment.ingr.in_(ingredient_list)).all()
    #         except:
    #             abort(404, message="No recipes with given ingredients!")
    #     else:
    #         return -1       #ERROR!!
