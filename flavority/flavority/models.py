
from binascii import hexlify
from datetime import datetime, timezone, date
from hashlib import sha256
import json
from re import compile as Regex
from os import urandom
import traceback

from flavority import app
from flavority.auth.mixins import UserMixin

db = app.db

#Associations aka Logic tables (many-to-many connections)
#DEL -> te takie inne niebieskie tabelki w uml'u, dla mnie to one sa niebieskie ale pewnie jakos inaczej ten kolor sie zwie, whatever
#Table will connect Ingredients with Recipes
class IngredientAssociation(db.Model):

    __tablename__ = 'IngredientAssociation'
    
    id = db.Column(db.Integer, primary_key = True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('Recipe.id'))
    ingredient_unit_id = db.Column(db.Integer, db.ForeignKey('IngredientUnit.id'))
    amount = db.Column(db.Integer)

    ingredient_unit = db.relationship('IngredientUnit', backref=db.backref('ingredient_asso', lazy='dynamic'))

    def __init__(self, ingredient_unit, amount):
        self.ingredient_unit = ingredient_unit
        self.amount = amount    


class IngredientUnit(db.Model):

    __tablename__ = 'IngredientUnit'

    id = db.Column(db.Integer, primary_key = True)
    unit_id = db.Column(db.Integer, db.ForeignKey('Unit.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('Ingredient.id'))

    ingredient = db.relationship('Ingredient', backref=db.backref('ingredient_unit', lazy='dynamic'))
    unit = db.relationship('Unit')

    def __init__(self, ingredient, unit):
        self.ingredient = ingredient
        self.unit = unit    


tag_assignment = db.Table('tag_assignment',
                          db.Column('recipe', db.Integer, db.ForeignKey('Recipe.id')),
                          db.Column('tag', db.Integer, db.ForeignKey('Tag.id')))
favour_recipes = db.Table('favour_recipes',
                          db.Column('user', db.Integer, db.ForeignKey('User.id')),
                          db.Column('recipe', db.Integer, db.ForeignKey('Recipe.id')))
#End of associations declaration

def serialize_date(dt):

    return dt.isoformat()

def to_json_dict(inst, cls, extra_content={}):
    """
    Jsonify the sql alchemy query result.

    in extra_content you can put any stuff you want to have in your json
    e.g. sth that is not a column
    """
    convert = dict()
    convert[db.Date] = lambda dt: dt.isoformat()
    convert[db.DateTime] = lambda dt: dt.isoformat()
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if type(c.type) in convert.keys() and v is not None:
            try:
                d[c.name] = convert[type(c.type)](v)

            except:
                traceback.print_exc()
                d[c.name] = "Error:  Failed to covert using ", str(convert[type(c.type)])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    d.update(extra_content)
    #return json.dumps(d)
    return d


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

    TOKEN_LENGTH = 1024

    __tablename__ = "User"    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(EMAIL_LENGTH), unique = True, nullable = False)
    salt  = db.Column(db.String(PASSWORD_LENGTH), nullable = False)
    password = db.Column(db.String(PASSWORD_LENGTH), nullable = False)
    type = db.Column(db.Enum(*tuple(USER_TYPES.values()), name = USER_TYPE_ENUM_NAME), default = USER_TYPES[USER_TYPE_COMMON])
    register_date = db.Column(db.DateTime)
    last_seen_date = db.Column(db.DateTime)
    
#    token = db.Column(db.String(TOKEN_LENGTH), default=None)
    favourites = db.relationship('Recipe', secondary=favour_recipes, lazy='dynamic')

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
       
    def __init__(self, email, password, type = None, register_date = None, last_seen_date = None):
        # validate arguments
        if not User.is_valid_email(email): raise ValueError()
        
        # set fields values
        self.email = email
        self.salt = hexlify(User.gen_salt())
        self.password = User.hash_pwd(User.combine(self.salt, password.encode()))
        if type is not None and type in User.USER_TYPES: self.type = User.USER_TYPES[type]
        if register_date is None:
            self.register_date = datetime.now()
        if last_seen_date is None:
            self.last_seen_date = self.register_date

    def to_json(self):
        photo = Photo.query.filter(Photo.avatar_user_id == self.id).first();
        return {
            "id": self.id,
            "email": self.email,
            "register_date": self.register_date.isoformat(),
            "last_seen_date": self.last_seen_date.isoformat(),
            "recipes": self.recipes.count(),
            "comments": self.comments.count(),
            "average_rate": self.count_average_rate(),
            "avatar": photo.id if photo is not None else ""
        }

    def get_id(self):
        return self.id

    def count_average_rate(self):
        sum_rate = 0
        sum_count = 0
        for recipe in self.recipes:
            sum_rate += recipe.taste_comments * recipe.comments.count()
            sum_count += recipe.comments.count()
        if sum_count == 0:
            return 0
        else:
            return sum_rate/sum_count
            
    def __repr__(self):
        return '<User: %r, with password: %r and email: %r>' % (self.id,  self.password, self.email)
#End of 'User' class declaration


#Class represents the recipe's object with name 'Recipe'
#Arg: db.Model - model from SQLAlchemy database
class Recipe(db.Model):
    
    DESCRIPTION_LENGTH = 120
    
    __tablename__ = 'Recipe'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dish_name = db.Column(db.String(DESCRIPTION_LENGTH))
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    creation_date = db.Column(db.DateTime)
    preparation_time = db.Column(db.SmallInteger)
    recipe_text = db.Column(db.Text)
    difficulty = db.Column(db.Float)
    taste_comments = db.Column(db.Float)
    difficulty_comments = db.Column(db.Float)
    eventToAdminControl = db.Column(db.Boolean)
    portions = db.Column(db.SmallInteger)

    author = db.relationship('User', backref=db.backref('recipes', lazy='dynamic'))
    ingredients = db.relationship('IngredientAssociation', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=tag_assignment, backref=db.backref('recipes', lazy='dynamic'))

    def __init__(self, dish_name, preparation_time, recipe_text, portions, difficulty, author_id, creation_date=None):
        self.dish_name = dish_name
        if creation_date is None:
            self.creation_date = datetime.now()
        self.preparation_time = preparation_time
        self.recipe_text = recipe_text
        self.portions = portions
        self.author_id = author_id
        self.difficulty = difficulty
        self.taste_comments = 0;
        self.difficulty_comments = 0;
    
    def __repr__(self):
        return '<Recipe name : %r, posted by : %r>' % (self.dish_name, self.author_id)

    def to_json_short(self, get_photo=None):
        if get_photo is None: get_photo = lambda x: x.id
        return {
            "id": self.id,
            "dishname": self.dish_name,
            "creation_date": str(self.creation_date),
            "photos": list(map(lambda x: get_photo(x), self.photos)),
            "rank": self.taste_comments if self.taste_comments is not None else 0.0,
            "tags": [i.json for i in self.tags],
        }

    def to_json(self):
        extra_content = {}
        tags = {} if self.tags is None else {'tags': [i.json for i in self.tags]}
        extra_content.update(tags)
        ingredients = {} if self.ingredients is None else \
            {'ingredients': [{"unit_name":i.ingredient_unit.unit.unit_name,"ingr_name": i.ingredient_unit.ingredient.name, "amount": i.amount} for i in self.ingredients]}
        extra_content.update(ingredients)
        extra_content.update({"photos": list(map(lambda x: x.id, self.photos))})
        extra_content.update({'author_name': self.author.email})                
        return to_json_dict(self, self.__class__, extra_content)

    
    def count_taste(self):
        sum = 0
        for comment in self.comments:
            sum += comment.taste
        if (self.comments.count() == 0):
            self.taste_comments = 0
        else:
            self.taste_comments = sum/self.comments.count()

    def count_difficulty(self):
        sum = 0
        for comment in self.comments:
            sum += comment.difficulty
        if (self.comments.count() == 0):
            self.difficulty_comments = 0
        else:
            self.difficulty_comments = sum/self.comments.count()
            
#End of 'Recipe' class declaration


#Class represents the Comment's object with name 'Comment'
#Arg: db.Model - model from SQLAlchemy database
class Comment(db.Model):
    
    COMMENT_TITLE_LENGTH = 120
    
    __tablename__ = 'Comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text)
    taste = db.Column(db.Float)
    difficulty = db.Column(db.Float)
    date = db.Column(db.DateTime)    
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    author = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))        #DELmany to one z comment do usera
    
    recipe_id = db.Column(db.Integer, db.ForeignKey('Recipe.id'))
    recipe = db.relationship('Recipe', backref=db.backref('comments', lazy='dynamic'))       #DElmany to one z comment do recipe
    
    def __init__(self, text, taste, difficulty, author_id, recipe_id, date=None):
        self.text = text
        self.taste = taste
        self.difficulty = difficulty
        self.author_id = author_id
        self.recipe_id = recipe_id
        if date is None:
            self.date = datetime.now()
   
    def __repr__(self):
        return '<Commented by: %r,to recipe: %r, with text: %r>' % (self.author_id, self.recipe_id , self.text)
    
    def to_json(self):
        photo = Photo.query.filter(Photo.avatar_user_id == self.author.id).first();
        extra_content = {}
        extra_content.update({'author_name': self.author.email})                
        extra_content.update({'author_avatar': photo.id if photo is not None else ""})                
        extra_content.update({'recipe_name': self.recipe.dish_name})                
        return to_json_dict(self, self.__class__, extra_content)
    
#End of 'Comment' class declaration


#Class represents the Rate object with name 'Rate'
#Arg: db.Model - model from SQLAlchemy database
class Rate(db.Model):
    __tablename__ = 'Rate'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    author = db.relationship('User', backref=db.backref('rates', lazy='dynamic'))       #DELmany to one z rate do usera
    recipe_id = db.Column(db.Integer, db.ForeignKey('Recipe.id'))
    recipe = db.relationship('Recipe', backref=db.backref('rates', lazy='dynamic'))       #DELmany to one z comment do recipe
    taste_rate = db.Column(db.SmallInteger)
    difficulty_rate = db.Column(db.SmallInteger)
    
    def __init__(self, taste, difficulty, author, recipe):
        self.taste_rate = taste
        self.difficulty_rate = difficulty
        self.author = author
        self.recipe = recipe
    
    def __repr__(self):
        return '<Rate from userID : %r, to recipeID : %r, taste : %r, difficulty : %r>' % (self.author_id, self.recipe_id, self.taste_rate, self.difficulty_rate)
#End of 'Rate' class declaration


#Class represents the Ingredient's object with name 'Ingredient'
#Arg: db.Model - model from SQLAlchemy database
class Ingredient(db.Model):
    
    INGREDIENT_NAME_LENGTH = 100
    
    __tablename__ = 'Ingredient'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(INGREDIENT_NAME_LENGTH))
#    unit_id = db.Column(db.Integer, db.ForeignKey('Unit.id'))
#    unit = db.relationship('Unit', backref=db.backref('units', lazy='dynamic'))
        
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return '<Ingredient\'s name : %r>' % self.name
    
#End of 'Ingredient' class declaration


#Class represents the Unit's object with name 'Unit'
#Arg: db.Model - model from SQLAlchemy database
class Unit(db.Model):
    
    UNIT_NAME_LENGTH = 40
    
    __tablename__ = 'Unit'
    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(UNIT_NAME_LENGTH), unique=True) #DELtak mi sie wydaje :P
    unit_value = db.Column(db.Float)
    other_id = db.Column(db.Integer, db.ForeignKey('Unit.id'))      #DELnie do konca zalapalem czemu, ale to musi tu zostac
    others = db.relationship('Unit', remote_side=[id])              #DELwedle wszelkich znakow w internetach ta relacja many to one powinna chodzic
    #DELsee -> Adjacency List Relationships at SQLAlchemy
    def __init__(self, unit_name, unit_value, others):
        self.unit_name = unit_name
        self.unit_value = unit_value
        self.others = others
    
    def __repr__(self):
        return '<Unit : %r, with value : %r>' % (self.unit_name, self.unit_value)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.unit_name,
        }
#End of 'Unit' class declaration


#Class represents the Tag's object with name 'Tag'
#Arg: db.Model - model from SQLAlchemy database
class Tag(db.Model):
    
    TAG_NAME_LENGTH = 40
    TAG_TYPE_LENGTH = 39
    
    __tablename__ = 'Tag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(TAG_NAME_LENGTH), unique=True)
    type = db.Column(db.String(TAG_TYPE_LENGTH))    # FIXME: what's this?
    
    def __init__(self, name, type=None):
        self.name = name
        self.type = type
    
    def __repr__(self):
        return '<Tag name : %r and type : %r>' % (self.name, self.type)

    @property
    def json(self):
        return to_json_dict(self, self.__class__)
#End of 'Tag' class declaration
#EOF


class Photo(db.Model):
    '''
    This class is a model for table containg photos used by recipes.

    Each recipe can have many photos, but any photo can only have one recipe. Photos should be stored as Base64 encoded
    strings with a proper format column set.
    '''

    DATA_ENCODED_LENGTH = 1 * 1024 * 1024   # 1 MB

    FORMAT = 'jpeg'

    __tablename__ = 'Photo'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('Recipe.id'), nullable=True)
    avatar_user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    full_data = db.Column(db.LargeBinary, nullable=False)
    mini_data = db.Column(db.LargeBinary, nullable=True)

    recipe = db.relationship('Recipe', backref=db.backref('photos', lazy='dynamic'))
    avatar_user = db.relationship("User")

    @staticmethod
    def supported_formats():
        return Photo.FORMAT_ENUM

    def is_attached(self):
        return self.recipe_id is not None or self.avatar_user_id is not None


