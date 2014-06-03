
from flask.ext.restful import Resource, reqparse
from flask_restful import abort
from sqlalchemy.exc import SQLAlchemyError

from functools import reduce

from . import lm, app
from .models import Comment, Recipe
from .util import Flavority, ViewPager


##Class that contains comment's methods such as:
#get,
#post,
#delete,
#put
#and many more needed in connection with website.
class Comments(Resource):

    ##Returns fields given in parser
    #Fields needed for comment:
    #id - user id,
    #author_id - comment's author id
    #recipe_id - id of commented recipe
    #text - comment's body (held as a markdown)
    #difficulty - voted recipe's difficulty in making
    #taste - voted recipe's taste
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

    ##Returns fields given in parser (to display comments on several pages if needed).
    #Fields:
    #recipe_id - ID of recipe in database
    #page - number of a page to display
    #limit - amount of comments per page
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

        parser = reqparse.RequestParser()
        parser.add_argument('about_me', type=cast_bool, default=False)
        parser.add_argument('my_comments', type=cast_bool, default=False)
        parser.add_argument('recipe_id', type=int, default=None)
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('limit', type=int, default=10)
        return parser.parse_args()

    #Implemented to get all User's comments
    @staticmethod
    def get_author_comments(author_id):
        try:
            return Comment.query.filter(Comment.author_id == author_id)
        except:
            abort(404, message="Author with id: {} has no comments!".format(author_id))

    ##Implemented to get all Recipe's comments
    @staticmethod
    def get_recipe_comments(recipe_id):
        try:
            return Comment.query.filter(Comment.recipe_id == recipe_id)
        except:
            abort(404, message="Recipe with id: {} has no comments yet!".format(recipe_id))

    ##Implemented to get specific comment with given comment_id, author_id and recipe_id
    @staticmethod
    def get_comment(comment_id, author_id, recipe_id):
        try:
            return Comment.query.filter(Comment.id == comment_id, Comment.author_id == author_id, Comment.recipe_id == recipe_id).one()
        except:
            abort(404, message="Comment with id: {} does not exist!".format(comment_id))

    ##Method implemented to return specific comment with given comment_id, author_id and recipe_id
    @staticmethod
    def get_user_recipes_comments(user):
        try:
            return reduce( lambda q1, q2: q1.union(q2), [ recipe.comments for recipe in user.recipes] )
        except BaseException as e:
            app.logger.error(e)
            abort(404, message="Author with id: {} has no comments!".format(user.id))

    ##Method implemented to handle assessments given while comment POST.
    #It prevents from:
    #posting without difficulty chosen,
    #posting without taste assessment,
    #posting with no text,
    #posting for a bad recipe ids
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

    ##Handles options for HTTP request
    def options(self):
        return None

    ##Method handles comment deletion:
    #Arguments needed:
    #comment_id - ID of comment to delete,
    #author_id - ID of author that wants to delete comment,
    #recipe_id - ID of recipe which was commented
    #Method prevents from deleting someones else comment.
    #It may return failure() if deletion was unsuccessful.
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

    ##Method handles comment edition
    #Arguments:
    #comment_id - ID of comment to edit,
    #new_text - new comment's text
    #Warning: You cannot change given difficulty or taste assessment!
    #It may return failure() it action will fail.
    @lm.auth_required
    def put(self, comment_id, new_text):
        comment = self.get_comment(comment_id)
        comment.text = new_text
        try:
            app.db.session.commit()
        except SQLAlchemyError:
            app.db.session.rollback()
            return Flavority.failure()
        return Flavority.success()

    ##Method handles HTTP GET statement.
    def get(self):
        args = self.parse_get_arguments()

        query = Comment.query
        user = lm.get_current_user()
        
        if args['about_me'] and user is not None:
            query = self.get_user_recipes_comments(user)

        if args['recipe_id'] is not None:
            query = query.filter(Comment.recipe_id == args['recipe_id'])

        if args['my_comments'] and user is not None:
            query = query.filter(Comment.author_id == user.id)
            
        query = query.order_by(Comment.date.desc())
        totalElements = query.count()
        query = ViewPager(query, args['page'], args['limit'])

        return {
            'comments': [c.to_json() for c in query.all()],
            'totalElements': totalElements,
        }

#    @lm.auth_required
    ##Method handles HTTP POST statement.
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
            app.logger.debug('No user has been detected! For debug purposes using user: {}'.format(user))

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
