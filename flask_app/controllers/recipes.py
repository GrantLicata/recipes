from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.recipe import Recipe
from flask_app.models.user import User
from pprint import pprint
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/recipes')
def profile():
    if session == {} or False:
        return redirect('/')
    list_of_recipes = Recipe.get_all()
    return render_template("table.html", all_recipes = list_of_recipes)

@app.route("/recipes/new")
def new_recipe():
    return render_template("new_recipe.html")

@app.route("/recipes/edit/<int:id>")
def edit_recipe(id):
    data = {
        "id": id
    }
    selected_recipe = {}
    recipe_object_list = Recipe.get_all()
    for recipe in recipe_object_list:
        if recipe.id == id:
            selected_recipe = recipe
            print(selected_recipe)
    under_30_option = selected_recipe.under_30
    return render_template("edit_recipe.html", recipe = selected_recipe, radio_option = under_30_option)

@app.route("/recipes/card/<int:id>")
def recipe_details(id):
    recipe_data = {
        "id": id
    } 
    user_id = {
        "id": session["user_id"]
    }
    return render_template("recipe.html", recipe = Recipe.get_one(recipe_data), user = User.get_by_id(user_id))

@app.route('/recipes/create', methods=["POST"])
def create_recipe():
    print("--------------------------------- mark")
    print("This is your user id:", session["user_id"])
    data = {
        "name": request.form["name"],
        "description" : request.form["description"],
        "instructions": request.form["instructions"],
        "date_cooked": request.form["date_cooked"],
        "under_30": request.form["under_30"],
        "user_id": session["user_id"]
    }
    print(data['under_30'])
    validation_data = {
        "name": request.form["name"],
        "description" : request.form["description"],
        "instructions": request.form["instructions"]
    }
    # Validaitons ---<>
    if not Recipe.validate_recipe(data): 
        return redirect('/recipes/new')
    Recipe.save(data)
    return redirect('/recipes')

@app.route('/recipes/update/<int:id>', methods=["POST"])
def update_recipe(id):
    data = {
        "id": id,
        "name": request.form["name"],
        "description" : request.form["description"],
        "instructions": request.form["instructions"],
        "date_cooked": request.form["date_cooked"],
        "under_30": request.form["under_30"],
        "user_id": session["user_id"]
    }
    # Validaitons ---<>
    if not Recipe.validate_recipe(data): 
        return redirect(f'/recipes/edit/{id}')
    Recipe.update(data)
    return redirect('/recipes')

@app.route('/recipe/delete/<int:id>', methods=["POST"])
def delete_recipe(id):
    data = {
        "id": id
    }
    print(data)
    Recipe.delete(data)
    return redirect('/recipes')

@app.route('/favorite/add', methods=["POST"])
def create_favorite():
    data = {
        "user_id": session["user_id"],
        "recipe_id" : request.form["recipe_id"],
    }
    User.new_favorite(data)
    return redirect(f'/recipes/card/{request.form["recipe_id"]}')

@app.route('/favorite/delete', methods=["POST"])
def delete_favorite():
    data = {
        "user_id": session["user_id"],
        "recipe_id": request.form["recipe_id"]
    }
    print(data)
    User.delete_favorite(data)
    return redirect(f'/recipes/card/{request.form["recipe_id"]}')

@app.route('/favorite/delete/favorites', methods=["POST"])
def delete_favorite_2():
    data = {
        "user_id": session["user_id"],
        "recipe_id": request.form["recipe_id"]
    }
    print(data)
    User.delete_favorite(data)
    return redirect('/favorites')

@app.route('/favorites')
def favorites():
    data = {
        "id": session["user_id"]
    }
    user = User.get_one_with_favorites(data)
    return render_template("favorites.html", favorites = user.favorites)


@app.route('/my_recipes')
def my_recipes():
    data = {
        "id": session["user_id"]
    }
    user = User.get_one_with_recipes(data)
    return render_template("my_recipes.html", my_recipes = user.recipes)