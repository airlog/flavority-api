
import os.path

##This is application's default configuration.

##Variable that determines mode of app deployment
DEBUG = True
##Variable that represents app secret key
SECRET_KEY = "totally random bytes"  # TODO: generate random bytes
##Variable that represents app temporary directory
TEMPDIR = 'tmp/'
##Variable that represents app root directory
APPLICATION_ROOT = os.path.curdir
##Variable that represents database path
SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(
        os.path.abspath(APPLICATION_ROOT),
        'test.db'))
