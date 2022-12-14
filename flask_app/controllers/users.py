from flask import render_template, redirect, request, session, flash
from flask_app import app
from pprint import pprint
from flask_app.models.recipe import Recipe
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    return render_template("login.html")

@app.route('/register', methods=["POST"])
def register():
    pprint(request.form)
    if not User.validate_user(request.form): 
        return redirect('/')
    data = {
        "first_name": request.form["first_name"],
        "last_name" : request.form["last_name"],
        "email": request.form["email"],
        "password" : bcrypt.generate_password_hash(request.form['password'])
    }
    session['user_id'] = User.save(data)
    return redirect('/recipes')

### loging In
@app.route('/login', methods=['POST'])
def login():
    print("---> This is the form data:", request.form)
    data = { 
        "email" : request.form["email"] 
        }
    user_in_db = User.get_by_email(data)
    if not user_in_db:
        flash("Invalid Email/Password")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password")
        return redirect('/')
    session['user_id'] = user_in_db.id
    session['first_name'] = user_in_db.first_name
    session['last_name'] = user_in_db.last_name
    return redirect("/recipes")

### Loging Out
@app.route('/logout')
def clear_session():
    session.clear()
    print(session)
    return render_template("login.html")


