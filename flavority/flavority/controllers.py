
from flask import g

from flavority import app, lm
from flavority.models import User


@lm.user_loader
def get_user(id):
    return User.query.get(id)
    
@lm.user_authenticator
def login(email, pwd):
    user = User.query.filter(User.email == email).first()
    if user is not None and user.password == User.hash_pwd(User.combine(user.salt, pwd.encode())): return user

@app.before_request
def retrieve_user():
    g.user = lm.get_current_user()
