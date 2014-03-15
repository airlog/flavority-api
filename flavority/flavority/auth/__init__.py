
def Auth(app, **kwargs):
    from flask import Blueprint
    
    from .blueprint import UserManager
    
    blueprint = Blueprint("LoginManager", __name__)
    app.register_blueprint(blueprint, **kwargs)
        
    return UserManager()

