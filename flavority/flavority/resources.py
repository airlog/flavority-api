
from . import app
from .recipes import RecipesWithId, Recipes, RecipesAdvancedSearch
from .signing import Signup, Signin
from .comments import Comments
from .tags import TagsResource
from .ingredients import IngredientsResource
from .photos import PhotoResource
from .units import UnitResource
from .users import UserById
from .favorite import FavoriteRecipes


app.restapi.add_resource(Signup, "/auth/signup")
app.restapi.add_resource(Signin, "/auth/signin")

app.restapi.add_resource(Recipes, "/recipes/")
app.restapi.add_resource(RecipesWithId,"/recipes/<int:recipe_id>")
app.restapi.add_resource(RecipesAdvancedSearch, "/recipes/advanced")


app.restapi.add_resource(Comments, '/comments/')
app.restapi.add_resource(TagsResource, '/tags/')
app.restapi.add_resource(IngredientsResource, '/ingredients/')
app.restapi.add_resource(UnitResource, '/units/')

app.restapi.add_resource(PhotoResource,
                        '/photos/',
                       '/photos/<int:photo_id>/')
                         
app.restapi.add_resource(UserById, "/users", "/users/<int:user_id>")

app.restapi.add_resource(FavoriteRecipes, "/favorite/","/favorite/<int:recipe_id>")

