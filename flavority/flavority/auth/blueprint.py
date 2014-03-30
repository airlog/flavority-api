
from functools import wraps

from flask import abort, request
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature

from .mixins import AnonymousMixin, UserMixin


class UserManager:

    USER_ID = 'uid'
    TOKEN_HEADER = "X-Flavority-Token"
    
    def __init__(self, secret_key, *args, **kwargs):
        if not isinstance(secret_key, str):
            raise TypeError()
        self.secret_key = secret_key

        # function called when retrieving UserID from session
        # should accept a single argument which will precisely identify the user
        self.user_loader_func = None
        
        # function called when authenticating user credentials
        # arguments depend on the user (forwarding them)
        self.user_auth_func = None

    def generate_token(self, userMixin, expiration=900):
        if not isinstance(userMixin, UserMixin):
            raise TypeError()
        s = TimedJSONWebSignatureSerializer(self.secret_key, expires_in=expiration)
        return s.dumps({
            self.USER_ID: userMixin.get_id(),
        })

    def get_current_user(self):
        s = TimedJSONWebSignatureSerializer(self.secret_key)
        try:
            token = request.headers[self.TOKEN_HEADER]
        except KeyError:
            return None

        # decode the token to access user identification data
        try:
            data = s.loads(token)
        except SignatureExpired:
            abort(401)
        except BadSignature:
            return None
        return self.user_loader_func(data[self.USER_ID])

    def login_user(self, *args, **kwargs):
        """
        Uses *user_auth_func* with arguments forwarded from this method's call to retrieve user object
        based on some data provided by the user (eg. a login form).
        
        Function used as *user_auth_function* should return an object with interface defined by
        **auth.mixins.UserMixin** class.
        
        Returns a user object on successful login or *None* if no user object can be found for provided
        credentials.
        """
        user = self.user_auth_func(*args, **kwargs)
        if user is None or isinstance(user, AnonymousMixin) or user == AnonymousMixin:
            return None
        return user
    
    ###
    ### decorators  
    ###          
    def user_loader(self, fn):
        """
        Use this decorator to specify a function that retrieves User object based on a unique ID.
        """
        self.user_loader_func = fn
        return fn
        
    def user_authenticator(self, fn):
        """
        Use this decorator to specify a function that retrieves User object based on data provided
        by a user (eg. with a login form).
        """
        self.user_auth_func = fn
        return fn

    def auth_required(self, fn):
        """
        Use this decorator to specify a resource which should be accessed only by authenticated users.
        """
        @wraps(fn)
        def decorated(*args, **kwargs):
            user = self.get_current_user()
            if user is None or isinstance(user, AnonymousMixin): abort(403)
            return fn(*args, **kwargs)
        return decorated

