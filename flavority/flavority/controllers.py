
from flask import g

from flavority import app, lm
from flavority.models import User


##Method returns user ID.
@lm.user_loader
def get_user(id):
    return User.query.get(id)


##Method handles user log in.
#Arguments:
#email - user's email
#pwd - users password
@lm.user_authenticator
def login(email, pwd):
    user = User.query.filter(User.email == email).first()
    if user is not None and user.password == User.hash_pwd(User.combine(user.salt, pwd.encode())): return user


##Method returns current user
@app.before_request
def retrieve_user():
    g.user = lm.get_current_user()


##Method that allows for Cross-Origin on server
@app.after_request
def crossorigin(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = ','.join([
        'X-Requested-With',
        'X-Flavority-Token',
        'Content-Type',
    ])
    return response
