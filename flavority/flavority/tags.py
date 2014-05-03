
from flask.ext.restful import Resource
from sqlalchemy import desc, func

from . import app
from .models import Tag, tag_assignment
from .util import Flavority


# TODO: moze by tak klient mowil ile chce tagow?
# (do rozpatrzenia sposób przekazania: przez URL czy argument get)
class TagsResource(Resource):

    TAGS_LIMIT = 30

    def get(self):
        '''
        Returns a list of TAGS_LIMIT most used tags in the following convention:
            ...
            tags: [
                {
                    'id': {{ tagId }},
                    'name': {{ tagName }},
                    'count': {{ recipesTaggedCount }},
                },
                ...
            ]
            ...
        '''

        # this query counts how many recipes are tagged by every tag (by id)
        # then there are sorted, in descending order, by a number of recipes tagged
        # and limited to the predefined number
        # in order to get tag's name they are also joined with Tag object
        tags = app.db.session\
            .query(tag_assignment.columns.tag, Tag.name, func.count(tag_assignment.columns.tag))\
            .join(Tag, tag_assignment.columns.tag == Tag.id)\
            .group_by(tag_assignment.columns.tag)\
            .order_by(desc(func.count(tag_assignment.columns.tag)))\
            .limit(self.TAGS_LIMIT)\
            .all()

        return Flavority.success(tags=[{'id': tag[0], 'name': tag[1], 'count': tag[2]} for tag in tags])
