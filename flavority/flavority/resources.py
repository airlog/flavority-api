
from flavority import app
from .signing import Signup, Signin


app.restapi.add_resource(Signup, "/auth/signup")
app.restapi.add_resource(Signin, "/auth/signin")

