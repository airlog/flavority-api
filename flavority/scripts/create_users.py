
from argparse import ArgumentParser
from json import loads
from sys import exit
from base64 import b64encode, b64decode

import flavority
from flavority.models import User, Recipe, Photo
from flavority.photos import PhotoResource


__author__  = "Joanna Cisło"
__desc__    = """Create users."""

KEY_FULL_SIZE = 'full-size'
KEY_MINI_SIZE = 'mini-size'


def add_users_to_database(db, n):

    
    photo_bytes = None
    with open("photo.jpg", "rb") as file: photo_bytes = file.read()
    
    files = PhotoResource.encode_image(photo_bytes)
    full_data = b64encode(files[KEY_FULL_SIZE])
    mini_data = b64encode(files[KEY_MINI_SIZE])
    
    users = User.query.all()
    start = len(users)
    for i in range(start,start+n):
        user = User('user{}@gmail.com'.format(i), '123')
        db.session.add(user)
        
        photo = Photo()
        photo.full_data = full_data
        photo.mini_data = mini_data
        photo.avatar_user_id = i
        db.session.add(photo)
        
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
        flavority.app.db.create_all()
        add_users_to_database(flavority.app.db, args.amount)
    exit(0)
