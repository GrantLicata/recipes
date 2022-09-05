from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash 
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

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.db).query_db(query)
        data = []
        for item in results:
            data.append( cls(item) )
        return data

    @classmethod
    def save(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password ,created_at, updated_at) VALUES ( %(first_name)s , %(last_name)s , %(email)s , %(password)s, NOW() , NOW() );"
        result = connectToMySQL(cls.db).query_db( query, data )
        print(result)
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
        users = User.get_all()
        for user in users:
            if user.email == data['email']:
                flash("Email already exists.")
                is_valid = False
        if len(data['email']) < 1:
            flash("Email is required.")
            is_valid = False
        return is_valid

    @staticmethod
    def validate_password(passwords):
        is_valid = True
        if passwords['password'] != passwords['confirm_password']:
            flash("Passwords must be the same.")
            is_valid = False
        if len(passwords['password']) < 8:
            flash("Passwords must be longer than 8 characters.")
            is_valid = False
        return is_valid