from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user
import re
from pprint import pprint

# Validation schematics
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Recipe:
    # Enter database reference below
    db = "recipes"
    def __init__(self ,data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date_cooked = data['date_cooked']
        self.under_30 = data['under_30']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.users_who_favorited = []
        self.user_ids_who_favorited = []
        self.author = None

    # ||| Multi Join Tables n:n ||| -> This should be stored within the many side of models and accompanied by class attributes of:
    # "self.users_who_liked = []"
    # "self.user_ids_who_liked = []"
    # "self.author = None" 
    # With these in place, you are now capable of gathering all the data needed.Cascase must be turned on for the Users side in the ERD.
    @classmethod
    def get_all(cls):
        query = """SELECT * FROM recipes 
        JOIN users AS authors ON recipes.user_id = authors.id
        LEFT JOIN favorites ON recipes.id = favorites.recipe_id
        LEFT JOIN users AS users_who_favorited ON favorites.user_id = users_who_favorited.id
        ;"""
        results = connectToMySQL(cls.db).query_db(query)
        recipes = []
        for row in results:
            new_recipe = True
            user_who_liked_data = {
                'id': row['users_who_favorited.id'],
                'first_name': row['users_who_favorited.first_name'],
                'last_name': row['users_who_favorited.last_name'],
                'email': row['users_who_favorited.email'],
                'password': row['users_who_favorited.password'],
                'created_at': row['users_who_favorited.created_at'],
                'updated_at': row['users_who_favorited.updated_at']
            }
            number_of_recipes = len(recipes)
            if number_of_recipes > 0:
                last_recipe = recipes[number_of_recipes - 1]
                if last_recipe.id == row['id']:
                    last_recipe.user_ids_who_favorited.append(row['users_who_favorited.id'])
                    last_recipe.users_who_favorited.append(user.User(user_who_liked_data))
                    new_recipe = False
            if new_recipe:
                recipe = cls(row)
                user_data = {
                    'id': row['authors.id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'password': row['password'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                recipe.author = user.User(user_data)
                if row['users_who_favorited.id']:
                    recipe.user_ids_who_favorited.append(row['users_who_favorited.id'])
                    recipe.users_who_favorited.append(user.User(user_who_liked_data))
                recipes.append(recipe)
        return recipes

# ||| Review the video to make all necessary adjustments to the get one method before using it to better display the recipe card within the applicaiton.
    @classmethod
    def get_one(cls, data):
        query = """SELECT * FROM recipes 
        JOIN users AS authors ON recipes.user_id = authors.id
        LEFT JOIN favorites ON recipes.id = favorites.recipe_id
        LEFT JOIN users AS users_who_favorited ON favorites.user_id = users_who_favorited.id
        WHERE recipes.id = %(id)s
        ;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        if len(results) < 1:
            return False

        new_recipe = True
        for row in results:
            if new_recipe:
                recipe = cls(row)
                user_data = {
                    'id': row['authors.id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'password': row['password'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                recipe.author = user.User(user_data)
                new_recipe = True
            if row['users_who_favorited.id']:
                user_who_liked_data = {
                    'id': row['users_who_favorited.id'],
                    'first_name': row['users_who_favorited.first_name'],
                    'last_name': row['users_who_favorited.last_name'],
                    'email': row['users_who_favorited.email'],
                    'password': row['users_who_favorited.password'],
                    'created_at': row['users_who_favorited.created_at'],
                    'updated_at': row['users_who_favorited.updated_at']
                }
                recipe.users_who_favorited.append(user.User(user_who_liked_data))
                recipe.user_ids_who_favorited.append(row['users_who_favorited.id'])
        return recipe

    @classmethod
    def save(cls, data):
        query = "INSERT INTO recipes (name, description, instructions, date_cooked, under_30, created_at, updated_at, user_id) VALUES ( %(name)s , %(description)s , %(instructions)s , %(date_cooked)s, %(under_30)s, NOW() , NOW(), %(user_id)s  );"
        result = connectToMySQL(cls.db).query_db( query, data )
        print("This is your saved recipe:", result)
        return result

    @classmethod
    def update(cls, data):
        query = "UPDATE recipes SET name = %(name)s, description = %(description)s, instructions = %(instructions)s, date_cooked = %(date_cooked)s, under_30 = %(under_30)s, user_id = %(user_id)s, updated_at = NOW() WHERE id = %(id)s;"
        print(query)
        result = connectToMySQL(cls.db).query_db( query, data )
        return result

    @classmethod
    def delete(cls, data):
        query = "DELETE FROM recipes WHERE id = %(id)s;"
        print("DELETE IS HAPPENING")
        result = connectToMySQL(cls.db).query_db( query, data )
        return result

    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(cls.db).query_db(query,data)
        print("-----<> Get_by_email result is:", result)
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_by_id(cls,data):
        query = "SELECT * FROM recipes WHERE id = %(id)s;"
        result = connectToMySQL(cls.db).query_db(query,data)
        if len(result) < 1:
            return False
        return cls(result[0])

    @staticmethod
    def validate_recipe(data):
        is_valid = True
        if len(data['name']) < 3:
            flash("Name must be longer than 3 characters.")
            is_valid = False
        if len(data['description']) < 3:
            flash("Description must be longer than 3 characters.")
            is_valid = False
        if len(data['instructions']) < 3:
            flash("Instructions must be longer than 3 characters.")
            is_valid = False
        if len(data['date_cooked']) < 1:
            flash("Date cooked must be selected.")
            is_valid = False
        if len(data['under_30']) < 1:
            flash("If under 30 minutes must be selected.")
            is_valid = False
        return is_valid
