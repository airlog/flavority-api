
import os.path

"""
This is application's default configuration.
"""

DEBUG = True
SECRET_KEY = "totally random bytes"  # TODO: generate random bytes
TEMPDIR = 'tmp/'
APPLICATION_ROOT = os.path.curdir

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(
        os.path.abspath(APPLICATION_ROOT),
        'test.db'))
