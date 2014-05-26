
from argparse import ArgumentParser
from json import loads

import flavority
from flavority.models import Recipe, Unit, Ingredient, IngredientAssociation, User, IngredientUnit


__author__	= "Joanna Cisło"
__desc__	= """Create database from recipes in json format."""


def add_recipes_to_database(db, recipes):
    from sys import stdout
    
    print(len(recipes))
    user = User('ala@gmail.com', '123')
    count = 0
    for r in recipes:
        count += 1
        stdout.write("\r{0:.2f}%".format(100.0*count/len(recipes)))
        try:
            recipe = Recipe(r['name'], r['time'], r['directions'], 1, None)
        except KeyError:
            recipe = Recipe(r['name'], '-', r['directions'], 1, None)
               
        for i in r['ingredients']:
            unit_parts = i['amount'].split()
            unit_name = unit_parts[-1]
            if len(unit_parts) == 1:
                unit_name = ''
            amount = unit_parts[0]
#            print(" '{}' x '{}' of '{}'".format(amount, unit_name, i['name']))
            
            ingr_unit = IngredientUnit\
                        .query\
                        .join(Unit, IngredientUnit.unit_id == Unit.id)\
                        .join(Ingredient, IngredientUnit.ingredient_id == Ingredient.id)\
                        .filter(Ingredient.name == i['name'], Unit.unit_name == unit_name)\
                        .first()
                        
            if ingr_unit is None:
                ingr = Ingredient.query.filter(Ingredient.name == i['name']).first()
                if ingr is None:
                    ingr = Ingredient(i['name'])
                    db.session.add(ingr)
                    db.session.commit()
                unit = Unit.query.filter(Unit.unit_name == unit_name).first()
                if unit is None:
                    unit = Unit(unit_name, None, None)
                    db.session.add(unit)
                    db.session.commit()
                ingr_unit = IngredientUnit(ingr,unit)
                db.session.add(ingr_unit)
                db.session.commit()
            
            recipe.ingredients.append(IngredientAssociation(ingr_unit, amount))
    
        db.session.add(recipe)
        db.session.commit()
    

parser = ArgumentParser(description = __desc__)
parser.add_argument("-i", "--input",
        type = str,
        dest = "file",
        help = "specify input file, by default application reads from STDIN"
    )

if __name__ == "__main__":
    args = parser.parse_args()
	
    text = None
    try:
        if args.file:
            with open(args.file, "r") as file: text = file.read()
    except IOError as e:
        print(e)
        exit(1)

    if text is None:
        file = stdin
        text = file.read()
    
    text = text.replace(']\n[' , ',\n')
    recipes = loads(text)
    flavority.app.db.drop_all()
    flavority.app.db.create_all()
    add_recipes_to_database(flavority.app.db, recipes)
