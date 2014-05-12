
from argparse import ArgumentParser
from json import loads
import random

import flavority
from flavority.models import Recipe, Comment, User


__author__	= "Joanna Cisło"
__desc__	= """Create database from recipes in json format."""


def add_comments_to_database(db, n):
    
    users = User.query.all()
    recipes = Recipe.query.all()
    comments = ['Very very very very very very very very very very very very very very very very very very very very very very very tasty', 'Not tasty', 'Good']
    rates = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    
    for i in range(n):
        user = random.sample(users, 1)[0]
        recipe = random.sample(recipes, 1)[0]
        text = random.sample(comments, 1)[0]
        taste = random.sample(rates, 1)[0]
        difficulty = random.sample(rates, 1)[0]
        comment = Comment(text, taste, difficulty, user.id, recipe.id)
        db.session.add(comment)
    db.session.commit()
    

parser = ArgumentParser(description = __desc__)
parser.add_argument("-n", "--number",
        type = int,
        dest = "amount",
        help = "amount of new comments"
    )

if __name__ == "__main__":
    args = parser.parse_args()
    
    if args.amount:
        flavority.app.db.create_all()
        add_comments_to_database(flavority.app.db, args.amount)
