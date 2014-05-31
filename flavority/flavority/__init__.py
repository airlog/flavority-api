
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

    def paths_to_abs(cfg):
        import os.path

        pathKeys = ['APPLICATION_ROOT', 'TEMPDIR']
        for key in pathKeys:
            cfg[key] = os.path.abspath(cfg[key])

    def create_directories(cfg):
        import os
        import os.path

        dirKeys = ['TEMPDIR']
        for key in dirKeys:
            if not os.path.exists(cfg[key]):
                os.mkdir(cfg[key])
            elif not os.path.isdir(cfg[key]):
                raise RuntimeError('Not a directory {}'.format(cfg[key]))

    if package is None: package = __name__

    a.config.from_object("{}.config".format(package))     # default settings
    try: a.config.from_envvar(__envvar__)                 # override defaults
    except RuntimeError: pass

    paths_to_abs(a.config)
    create_directories(a.config)


def load_database(a):
    a.db.create_all()


import flavority.models

load_config(app, package=__name__)
load_database(app)


from flavority.auth import Auth
lm = Auth(app)

import flavority.resources
import flavority.controllers
