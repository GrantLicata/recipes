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
        self.posted_by = None

    @classmethod
    def get_all_recipes_with_users(cls):
        query = "SELECT * FROM recipes JOIN users ON recipes.user_id = users.id;"
        results = connectToMySQL(cls.db).query_db(query)
        recipe_objects = []
        for row in results:
            recipe_object = cls(row)
            user_data = {
                'id': row["user_id"],
                'first_name': row["first_name"],
                'last_name': row["last_name"],
                'password': row["password"],
                'email': row["email"],
                'created_at': row["users.created_at"],
                'updated_at': row["users.updated_at"]
            }
            recipe_object.posted_by = user.User(user_data)
            recipe_objects.append( recipe_object )
        return recipe_objects

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