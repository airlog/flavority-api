
from flavority import app
from .recipes import RecipesWithId, Recipes
from .signing import Signup, Signin


app.restapi.add_resource(Signup, "/auth/signup")
app.restapi.add_resource(Signin, "/auth/signin")

app.restapi.add_resource(Recipes, "/recipes")
app.restapi.add_resource(RecipesWithId, "/recipes/<int:recipe_id>")

