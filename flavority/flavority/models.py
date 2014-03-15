
from binascii import hexlify
from hashlib import sha256
from re import compile as Regex
from os import urandom

from flavority import app
from flavority.auth.mixins import UserMixin

db = app.db

class User(db.Model, UserMixin):

    # should be sufficient
    EMAIL_LENGTH    = 128
    
    EMAIL_REGEX   = Regex(r'([A-Za-z._0-9]+)@([A-Za-z._0-9]{2,}.[a-z]{2,})')
    
    # maximum hash length: 512 b == to bytes => 64 B == base16 => 128 B
    # this will allow for quite nice changing between hash algorithms
    PASSWORD_LENGTH = 64 * 2
    
    # size (in bytes) of salt+password's hash
    HASH_SIZE   = 32
    
    # used by SQLAlchemy if native enums is supported by database
    USER_TYPE_ENUM_NAME = "UserType"

    # allowed user types keys
    USER_TYPE_COMMON    = "common"
    USER_TYPE_ADMIN     = "admin"
    
    # allowed user values
    USER_TYPES  = {
            USER_TYPE_COMMON: "COMMON",
            USER_TYPE_ADMIN: "ADMINISTRATOR"
        }
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(EMAIL_LENGTH), unique = True, nullable = False)
    salt  = db.Column(db.String(PASSWORD_LENGTH), nullable = False)
    password = db.Column(db.String(PASSWORD_LENGTH), nullable = False)
    type = db.Column(db.Enum(*tuple(USER_TYPES.values()), name = USER_TYPE_ENUM_NAME), default = USER_TYPES[USER_TYPE_COMMON])

    @staticmethod
    def gen_salt(length = HASH_SIZE):
        return urandom(length)
        
    @staticmethod
    def combine(salt, pwd):
        return salt + pwd

    @staticmethod
    def hash_pwd(bytes):
        return sha256(bytes).hexdigest()

    @staticmethod
    def is_valid_email(text):
        return User.EMAIL_REGEX.match(text) is not None
       
    def __init__(self, email, password, type = None):
        # validate arguments
        if not User.is_valid_email(email): raise ValueError()
        
        # set fields values
        self.email = email
        self.salt = hexlify(User.gen_salt())
        self.password = User.hash_pwd(User.combine(self.salt, password.encode()))
        if type is not None and type in User.USER_TYPES: self.type = User.USER_TYPES[type]

    def get_id(self):
        return self.id

