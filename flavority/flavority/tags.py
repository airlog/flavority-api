
from flask import request
from flask.ext.restful import Resource
from sqlalchemy import desc, func

from . import app
from .models import Tag, tag_assignment
from .util import Flavority


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

        try:
            limit = int(request.args.get('limit', self.TAGS_LIMIT))
            if limit <= 0: raise ValueError()
        except ValueError:
            limit = self.TAGS_LIMIT

        try:
            page = int(request.args.get('page', 1))
            if page <= 0: raise ValueError()
        except ValueError:
            page = 1
        # this query counts how many recipes are tagged by every tag (by id)
        # then there are sorted, in descending order, by a number of recipes tagged
        # and limited to the predefined number
        # in order to get tag's name they are also joined with Tag object
        tags = app.db.session\
            .query(tag_assignment.columns.tag, Tag.name, func.count(tag_assignment.columns.tag))\
            .join(Tag, tag_assignment.columns.tag == Tag.id)\
            .group_by(tag_assignment.columns.tag)\
            .order_by(desc(func.count(tag_assignment.columns.tag)))\
            .all()
        tags = tags[limit * (page - 1):limit * page]

        return Flavority.success(tags=[{'id': tag[0], 'name': tag[1], 'count': tag[2]} for tag in tags])
