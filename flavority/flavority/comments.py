
from flask.ext.restful import Resource, reqparse
from flask_restful import abort
from sqlalchemy.exc import SQLAlchemyError

from . import lm, app
from .models import Comment, Recipe
from .util import Flavority


class Comments(Resource):

    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, requred=True, help="comment id")
        parser.add_argument('author_id', type=int, required=True, help="comment author id")
        parser.add_argument('recipe_id', type=int, required=True, help="comment recipe id")
        parser.add_argument('text', type=str, required=True, help="comment text")
        parser.add_argument('difficulty', type=float, required=False, help="given difficulty")
        parser.add_argument('taste', type=float, required=False, help="given taste")

        return parser

    @staticmethod
    def parse_get_arguments():
        parser = reqparse.RequestParser()
        parser.add_argument('recipe_id', type=int, default=None)
        parser.add_argument('page', type=int, default=0)
        parser.add_argument('limit', type=int, default=10)
        return parser.parse_args()

    #Implemented to get all User's comments
    @staticmethod
    def get_author_comments(author_id):
        try:
            return Comment.query.filter(Comment.author_id == author_id)
        except:
            abort(404, message="Author with id: {} has no comments!".format(author_id))

    #Implemented to get all Recipe's comments
    @staticmethod
    def get_recipe_comments(recipe_id):
        try:
            return Comment.query.filter(Comment.recipe_id == recipe_id)
        except:
            abort(404, message="Recipe with id: {} has no comments yet!".format(recipe_id))

    #Implemented to get specific comment with given comment_id, author_id and recipe_id
    @staticmethod
    def get_comment(comment_id, author_id, recipe_id):
        try:
            return Comment.query.filter(Comment.id == comment_id, Comment.author_id == author_id, Comment.recipe_id == recipe_id).one()
        except:
            abort(404, message="Comment with id: {} does not exist!".format(comment_id))

<<<<<<< HEAD
    #Method to add new comment
    @lm.auth_required
    def post(self):
        args = Comments.get_form_parser().parse_args()
        
        comment = Comment(args.text, args.taste, args.difficulty, args.author_id, args.recipe_id)
            #Ew. tutaj można tworzyć strukturę Rate, aby nie tworzyć do tego js-ów w backbonie
        try:
            app.db.session.add(comment)
            app.db.session.commit()
        except SQLAlchemyError:
            app.db.session.rollback()
            return Flavority.failure(), 500
        return Flavority.success(), 201
=======
    @staticmethod
    def parse_post_arguments():
        def mark(x):
            f = float(x)
            if f in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
                return f
            raise ValueError('bad value')

        parser = reqparse.RequestParser()
        parser.add_argument('taste', type=mark, required=True,
                help='missing mark of a meal\'s taste')
        parser.add_argument('difficulty', type=mark, required=True,
                help='missing mark of a meal\'s preparation difficulty')
        parser.add_argument('text', type=str, required=True,
                help='any text content is required')
        parser.add_argument('recipe', type=int, required=True,
                help='missing recipe\'s id')
        return parser.parse_args()

    def options(self):
        return None
>>>>>>> master1

    #Method handles comment deletion
    @lm.auth_required
    def delete(self, comment_id, author_id, recipe_id):
        comment_to_delete = self.get_comment(comment_id, author_id, recipe_id) #If someone's user_id is different from author's id then \
                # comment shouldn't be found because comment_id was given
        try:
            app.db.session.delete(comment_to_delete)
            app.db.session.commit()
        except SQLAlchemyError:
            app.db.session.rollback()
            return Flavority.failure()
        return Flavority.success()

    #Method handles comment edition
    @lm.auth_required
    def put(self, comment_id, new_text):   #zakladam, ze nie mozna zmienic oceny tylko sam tekst komentarza!!
        comment = self.get_comment(comment_id)      #same note as in $delete$ method -> will search for proper comment (only author can edit)
        comment.text = new_text
        try:
            app.db.session.commit()
        except SQLAlchemyError:
            app.db.session.rollback()
            return Flavority.failure()
        return Flavority.success()

    def get(self):
        args = self.parse_get_arguments()

        query1, query2 = Comment.query, Comment.query
        if args['recipe_id'] is not None:
            query1, query2 = Recipe.query.get(args['recipe_id']).comments, Recipe.query.get(args['recipe_id']).comments
        query1 = query1.order_by(Comment.date.desc())
        query1 = query1.slice(args['page']*args['limit'], (1+args['page'])*args['limit'])

        return {
            'comments': [c.to_json() for c in query1.all()],
            'all': query2.count()
        }

#    @lm.auth_required
    def post(self):
        args = self.parse_post_arguments()
        user, recipe = lm.get_current_user(), Recipe.query.get(args.recipe)
        if recipe is None:
            return {
                'message': 'no such recipe with id {}'.format(args.recipe_id),
                'status': 404,
            }, 404

        # when @lm.auth_required is active this is needless
        if user is None:
            from flavority.models import User
            user = User.query.first()
            return abort(500)

        # creating new comment
        comment = Comment(args.text, args.taste, args.difficulty, user.get_id(), recipe.id)
        try:
            app.db.session.add(comment)
            app.db.session.commit()
            recipe.count_taste()
            recipe.count_difficulty()
            app.db.session.commit()
        except SQLAlchemyError as e:
            app.logger.error(e)
            return {
                'message': 'committing the transaction failed',
                'status': 500,
            }, 500

        return comment.to_json()


__all__ = ['Comments']
