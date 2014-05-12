
from argparse import ArgumentParser
from json import loads

import flavority
from flavority.models import User


__author__	= "Joanna Cisło"
__desc__	= """Create database from recipes in json format."""


def add_users_to_database(db, n):
    
    users = User.query.all()
    start = len(users)
    for i in range(start,start+n):
        user = User('user{}@gmail.com'.format(i), '123')
        db.session.add(user)
    db.session.commit()
    

parser = ArgumentParser(description = __desc__)
parser.add_argument("-n", "--number",
        type = int,
        dest = "amount",
        help = "amount of new users"
    )

if __name__ == "__main__":
    args = parser.parse_args()
    if args.amount:
    	add_users_to_database(flavority.app.db, args.amount)
