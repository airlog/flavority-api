
from argparse import ArgumentParser
from random import randint, sample
from sys import stderr, stdout, exit

from sqlalchemy.exc import SQLAlchemyError

from flavority import app
from flavority.models import Recipe, Tag


def parse_args():
    def cast_natural(x):
        try: i = int(x)
        except ValueError: return 1
        return i if i >= 1 else 1


    parser = ArgumentParser()
    parser.add_argument('amount', type=cast_natural,
                        help='number of tags to be generated and added')
    return parser.parse_args()


def generate_tags(amount, group_min=0, group_max=None, tag_name_base='Tag'):
    recipes = Recipe.query.all()
    if group_max is None: group_max = len(recipes) - 1

    stdout.write('Generating tags... \n')
    for i in range(amount):
        tag = Tag('{}{}'.format(tag_name_base, i + 1))
        group_size = randint(group_min, group_max)
        for recipe in sample(recipes, group_size):
            recipe.tags.append(tag)
            app.db.session.add(tag)
        percent = (i + 1) * 100 // amount
        stdout.write('{0:3}%\r'.format(percent))
    stdout.write('Done.\n')

    stdout.write('Committing changes...\n')
    try:
        app.db.session.commit()
    except SQLAlchemyError as e:
        stderr.write(e)
        return False
    stdout.write('Done.\n')

    return True


if __name__ == '__main__':
    args = parse_args()
    exit(0) if generate_tags(args.amount) else exit(1)
