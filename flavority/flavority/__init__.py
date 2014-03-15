
from flask import Flask, g, json
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api

__version__ = "0.1.0"
   
app = Flask(__name__)
app.db = SQLAlchemy(app)
app.restapi = Api(app)

from flavority.auth import Auth
lm = Auth(app)

import flavority.resources
import flavority.controllers
        
flavority.controllers.load_config(app, package = __name__)
flavority.controllers.load_database(app)
    
@app.route("/")
@lm.auth_required
def index():
    return json.jsonify(
            email = g.user.email,
            type = g.user.type,
        )

