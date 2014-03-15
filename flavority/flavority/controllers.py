
from flask import g

from flavority import app, lm
from flavority.models import User

__envvar__ = "FLAVORITY_SETTINGS"

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

def load_config(a, package = None):
    """
    Loading application configuration from environment variable or, if not set, from config file
    distributed with this module.
    
    :param a:   flask's application object
    """
    if package is None: package = __name__
    a.config.from_object("{}.config".format(package))     # default settings
    try: a.config.from_envvar(__envvar__)                 # override defaults
    except RuntimeError: pass

def load_database(a):
    a.db.drop_all()
    a.db.create_all()
    
