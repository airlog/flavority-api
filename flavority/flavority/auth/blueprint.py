
from binascii import hexlify
from functools import wraps
from os import urandom

from flask import abort, Blueprint, request

from .mixins import AnonymousMixin

class UserManager:
    
    TOKEN_LENGTH = 20
    TOKEN_HEADER = "X-Flavority-Token"
    
    def __init__(self, *args, **kwargs):
        self.users = {}

        # function called when retrieving UserID from session
        # should accept a single argument which will precisely identify the user
        self.user_loader_func = None
        
        # function called when authenticating user credentials
        # arguments depend on the user (forwarding them)
        self.user_auth_func = None
        
    def __in__(self, key):
        return key in self.users
    
    def __getitem__(self, key):
        try:
            if isinstance(key, str): return self.users[key]
        except KeyError: pass
        
    def generate_token(self, token_bytes = TOKEN_LENGTH):
        return hexlify(urandom(token_bytes)).decode()

    def register_user(self, user):
        if user.id in self.users.values(): raise ValueError()
        
        token = self.generate_token()
        while token in self.users: token = self.generate_token()
        self.users[token] = user.id
        
        return token
        
    def unregister_user(self):
        token = request.headers[self.TOKEN_HEADER]
        del self.users[token]
    
    def get_current_user(self):
        try:
            return self.user_loader_func(self.users[request.headers[self.TOKEN_HEADER]])
        except KeyError:
            pass
    
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
        if user is None or isinstance(user, AnonymousMixin) or user == AnonymousMixin: return None
        
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

