
from flask import Flask, g, json
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api

__version__ = "0.1.0"
__envvar__ = "FLAVORITY_SETTINGS"
   
app = Flask(__name__)
app.db = SQLAlchemy(app)
app.restapi = Api(app)

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

import flavority.models

load_config(app, package=__name__)
load_database(app)

from flavority.auth import Auth
lm = Auth(app)

import flavority.resources
import flavority.controllers


@app.route("/")
@lm.auth_required
def index():
    return json.jsonify(
            email = g.user.email,
            type = g.user.type,
        )

