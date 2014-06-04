
from flask import g

from flavority import app, lm
from flavority.models import User


@lm.user_loader
def get_user(id):
    """Should return specified user
    """
    return User.query.get(id)


@lm.user_authenticator
def login(email, pwd):
    """Handles sign in operation for users with given email and password
    """
    user = User.query.filter(User.email == email).first()
    if user is not None and user.password == User.hash_pwd(User.combine(user.salt, pwd.encode())): return user


@app.before_request
def retrieve_user():
    """Written to get correct user before request takes action
    """
    g.user = lm.get_current_user()


@app.after_request
def crossorigin(response):
    """Written in order to allow cross-origin request on server
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = ','.join([
        'X-Requested-With',
        'X-Flavority-Token',
        'Content-Type',
    ])
    return response
