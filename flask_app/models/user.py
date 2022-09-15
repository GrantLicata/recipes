from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import recipe
from flask import flash
from pprint import pprint
import re

# Validation schematics
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    # Enter database reference below
    db = "recipes"
    def __init__(self ,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password'] 
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.recipes = []
        self.favorites = [] 

    @classmethod
    def get_one_with_recipes(cls, data):
        query = """SELECT * 
        FROM users 
        JOIN recipes 
        ON recipes.user_id = users.id WHERE users.id = %(id)s
        ;"""
        results = connectToMySQL(cls.db).query_db( query, data )
        user = cls(results[0])
        # pprint(results, sort_dicts=False, width=1)
        for row in results:
            recipe_data = {
                "id": row['recipes.id'],
                "name": row['name'],
                "description": row['description'],
                "instructions": row['instructions'],
                "date_cooked": row['date_cooked'],
                "under_30": row['under_30'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at'],
                "posted_by": None
            }
            user.recipes.append( recipe.Recipe(recipe_data) )
        return user

    @classmethod
    def get_one_with_favorites(cls, data):
        query = """SELECT * 
        FROM users 
        LEFT JOIN favorites ON favorites.user_id = users.id 
        LEFT JOIN recipes ON favorites.recipe_id = recipes.id WHERE users.id = %(id)s
        ;"""
        results = connectToMySQL(cls.db).query_db( query, data )
        user = cls(results[0])
        # pprint(results, sort_dicts=False, width=1)
        for row in results:
            recipe_data = {
                "id": row['recipes.id'],
                "name": row['name'],
                "description": row['description'],
                "instructions": row['instructions'],
                "date_cooked": row['date_cooked'],
                "under_30": row['under_30'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at'],
                "posted_by": None
            }
            user.favorites.append( recipe.Recipe(recipe_data) )
        return user

    @classmethod
    def save(cls, data):
        query = """INSERT 
        INTO users (first_name, last_name, email, password ,created_at, updated_at) 
        VALUES ( %(first_name)s , %(last_name)s , %(email)s , %(password)s, NOW() , NOW() );"""
        result = connectToMySQL(cls.db).query_db( query, data )
        return result

    @classmethod
    def update(cls, data):
        query = "UPDATE users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s, updated_at = NOW() WHERE id = %(id)s;"
        print(query)
        result = connectToMySQL(cls.db).query_db( query, data )
        return result

    @classmethod
    def delete(cls, data):
        query = "DELETE FROM users WHERE id = %(id)s;"
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
        query = "SELECT * FROM users WHERE id = %(id)s;"
        result = connectToMySQL(cls.db).query_db(query,data)
        print("-----<> Get_by_id result is:", result)
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def new_favorite(cls,data):
        query = """INSERT 
        INTO favorites (user_id, recipe_id) 
        VALUES ( %(user_id)s , %(recipe_id)s );"""
        result = connectToMySQL(cls.db).query_db( query, data )
        return result

    @classmethod
    def delete_favorite(cls, data):
        query = "DELETE FROM favorites WHERE (user_id = %(user_id)s AND recipe_id = %(recipe_id)s);"
        print("This is the delete funcitons data:", data)
        result = connectToMySQL(cls.db).query_db( query, data )
        return result

    @staticmethod
    def validate_user(data):
        is_valid = True
        #First name validation
        if len(data['first_name']) < 2:
            flash("First name is required.")
            is_valid = False
        #Last name validation
        if len(data['last_name']) < 2:
            flash("Last name is required.")
            is_valid = False
        # Email validation
        if not EMAIL_REGEX.match(data['email']): 
            flash("Invalid email address!")
            is_valid = False
        users = User.get_all()
        for user in users:
            if user.email == data['email']:
                flash("Email already exists.")
                is_valid = False
        if len(data['email']) < 1:
            flash("Email is required.")
            is_valid = False
        if data['password'] != data['confirm_password']:
            flash("Passwords must be the same.")
            is_valid = False
        if len(data['password']) < 8:
            flash("Passwords must be longer than 8 characters.")
            is_valid = False
        return is_valid


    