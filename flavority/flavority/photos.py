
from base64 import b64encode, b64decode
from io import SEEK_SET
from tempfile import NamedTemporaryFile

from flask import abort, send_file
from flask.ext.restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError
from wand.image import Image

from . import app
from .models import Photo, Recipe


class PhotoResource(Resource):

    """This class handles request for images.
    """

    KEY_FULL_SIZE = 'full-size'
    KEY_MINI_SIZE = 'mini-size'

    @staticmethod
    def convert_image(image, format=Photo.FORMAT):
		"""Converts images
		"""
        return image.convert(format)

    @staticmethod
    def encode_image(image_binary, mini_size=(300, 300)):
		"""Encodes images
		"""
        assert isinstance(image_binary, bytes)

        with Image(blob=image_binary) as image:
            if image.format.lower() != format:
                image = PhotoResource.convert_image(image)
            mini_img = image.clone()
            mini_img.resize(*mini_size)
            full, mini = image.make_blob(), mini_img.make_blob()

        return {
            PhotoResource.KEY_FULL_SIZE: full,
            PhotoResource.KEY_MINI_SIZE: mini,
        }

    @staticmethod
    def parse_get_arguments():
		"""Written to parse arguments connected with GET request
		"""
        def cast_mini(x):
            if x.lower() == '': return True
            elif x.lower() == 'false': return False
            elif x.lower() == 'true': return True
            try:
                return bool(x)
            except ValueError:
                return False

        parser = reqparse.RequestParser()
        parser.add_argument('mini', type=cast_mini)
        return parser.parse_args()

    @staticmethod
    def parse_post_arguments():
		"""Written to parse arguments connected with POST request
		"""
        parser = reqparse.RequestParser()
        parser.add_argument('file', required=True, location='files')
        parser.add_argument('recipe_id', type=int)
        return parser.parse_args()

    def options(self, photo_id=None):
        return None

    def get(self, photo_id=None):
        """Returns a Base64 encoded JPEG image with supplied id from database.
			If such an row doesn't exists or supplied id is `None` than HTTP404 will be
			returned.
			If request has a `mini` GET parameter then it will return image's miniature.
        """

        if photo_id is None:
            return abort(404)

        args = self.parse_get_arguments()
        app.logger.info(args)
        image = Photo.query.get(photo_id)
        if image is None:
            return abort(404)

        file = NamedTemporaryFile(prefix='img{}'.format(photo_id), suffix='.jpg', dir=app.config['TEMPDIR'])
        file.write(b64decode(image.full_data if not args['mini'] else image.mini_data))
        file.seek(0, SEEK_SET)

        return send_file(file, mimetype='image/jpeg')

    def post(self, photo_id=None):
        """ Inserts new image to the database.
				This method expects two additional arguments:
				+ `file` - an image file transmitted with a request
				+ `recipe_id` - id of a recipe which owns the image
				Method returns a dictionary with a id of just created row.

				This method can be used only when no `photo_id` is specified. In other case
				HTTP405 is returned. It may also return HTTP500 when adding to the database
				fails.
        """

        if photo_id is not None:
            return abort(405)

        args = self.parse_post_arguments()
        file_bytes = args['file'].read()
        files = PhotoResource.encode_image(file_bytes)

        photo = Photo()
        photo.full_data = b64encode(files[self.KEY_FULL_SIZE])
        photo.mini_data = b64encode(files[self.KEY_MINI_SIZE])

        if args.recipe_id is not None:
            photo.recipe = Recipe.query.get(args['recipe_id'])

        try:
            app.db.session.add(photo)
            app.db.session.commit()
        except SQLAlchemyError as e:
            app.logger.error(e)
            app.db.session.rollback()
            return abort(500)

        return {
            'id': photo.id
        }


__all__ = ['PhotoResource']
