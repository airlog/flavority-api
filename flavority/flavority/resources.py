
from . import app
from .recipes import RecipesWithId, Recipes, MyRecipes
from .signing import Signup, Signin
from .comments import Comments
from .tags import TagsResource
from .ingredients import IngredientsResource
from .photos import PhotoResource
from .users import UserById


app.restapi.add_resource(Signup, "/auth/signup")
app.restapi.add_resource(Signin, "/auth/signin")

app.restapi.add_resource(Recipes, "/recipes/")
app.restapi.add_resource(RecipesWithId,"/recipes/<int:recipe_id>")
app.restapi.add_resource(MyRecipes, "/myrecipes/")


app.restapi.add_resource(Comments, '/comments/')
app.restapi.add_resource(TagsResource, '/tags/')
app.restapi.add_resource(IngredientsResource, '/ingredients/')

app.restapi.add_resource(PhotoResource,
                         '/photos/',
                         '/photos/<int:photo_id>/')
                         
app.restapi.add_resource(UserById, "/users", "/users/<int:user_id>")

