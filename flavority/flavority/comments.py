from flask.ext.restful import Resource, reqparse
from flask_restful import abort
from sqlalchemy.exc import SQLAlchemyError
from flavority import lm, app
from .models import Comment


class Comments(Resource):

    decorators = [lm.auth_required]

    @staticmethod
    def get_form_parser():
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, requred=True, help="comment id")
        parser.add_argument('author_id', type=int, required=True, help="comment author id")
        parser.add_argument('recipe_id', type=int, required=True, help="comment recipe id")
        parser.add_argument('title', type=str, required=True, help="comment title")
        parser.add_argument('text', type=str, required=True, help="comment text")

        return parser

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

    #TODO: Implementation of comment_post() method

    #Method handles comment deletion
    def delete(self, comment_id, author_id, recipe_id):
        comment_to_delete = self.get_comment(comment_id, author_id, recipe_id) #If someone's user_id is different from author's id then \
                # comment shouldn't be found because comment_id was given
        try:
            app.db.session.delete(comment_to_delete)
            app.db.session.commit()
        except SQLAlchemyError:
            app.db.session.rollback()
            return {"result": "failure"}
        return {"result": "success"}

    #Method handles comment edition
    def edit(self, comment_id, new_title, new_text):
        comment = self.get_comment(comment_id)      #same note as in $delete$ method -> will search for proper comment (only author can edit)
        comment.title = new_title
        comment.text = new_text
        try:
            app.db.session.commit()
        except SQLAlchemyError:
            app.db.session.rollback()
            return {"result": "failure"}
        return {"result": "success"}