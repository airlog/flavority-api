
from flask.ext.restful import Resource, reqparse
from sqlalchemy import desc, func

from . import app
from .models import Tag, tag_assignment
from .util import ViewPager


class TagsResource(Resource):

    GET_ITEMS_PER_PAGE = 30

    @staticmethod
    def parse_get_arguments():
        def cast_natural(x):
            try: i = int(x)
            except ValueError: return 1
            return i if i >= 1 else 1

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=cast_natural, default=1)
        parser.add_argument('limit', type=cast_natural, default=TagsResource.GET_ITEMS_PER_PAGE)
        return parser.parse_args()

    def options(self):
        return None

    def get(self):
        """
        Returns a list of TAGS_LIMIT most used tags in the following convention:
            ...
            [
                {
                    'id': {{ tagId }},
                    'name': {{ tagName }},
                    'count': {{ recipesTaggedCount }},
                },
                ...
            ]
        """
        args = self.parse_get_arguments()

        # this query counts how many recipes are tagged by every tag (by id)
        # then there are sorted, in descending order, by a number of recipes tagged
        # and limited to the predefined number
        # in order to get tag's name they are also joined with Tag object
        tags = app.db.session\
            .query(tag_assignment.columns.tag, Tag.name, func.count(tag_assignment.columns.tag))\
            .join(Tag, tag_assignment.columns.tag == Tag.id)\
            .group_by(tag_assignment.columns.tag)\
            .order_by(desc(func.count(tag_assignment.columns.tag)))
        tags = ViewPager(tags, page=args['page'], limit_per_page=args['limit']).all()

        return [{'id': tag[0], 'name': tag[1], 'count': tag[2]} for tag in tags]


__all__ = ['TagsResource']
