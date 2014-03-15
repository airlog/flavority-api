
from flavority import app
from .signing import Signup, Signin, Signout

app.restapi.add_resource(Signup, "/auth/signup")
app.restapi.add_resource(Signin, "/auth/signin")
app.restapi.add_resource(Signout, "/auth/signout")

