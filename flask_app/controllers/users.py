from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.recipe import Recipe
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    return render_template("login.html")

@app.route('/register', methods=["POST"])
def register():
    print(request.form)
    if not User.validate_user(request.form): 
        return redirect('/')
    data = {
        "first_name": request.form["first_name"],
        "last_name" : request.form["last_name"],
        "email": request.form["email"],
        "password" : bcrypt.generate_password_hash(request.form['password'])
    }
    User.save(data)
    return redirect('/recipes')

### loging In
@app.route('/login', methods=['POST'])
def login():
    print(request.form)
    data = { 
        "email" : request.form["email"] 
        }
    user_in_db = User.get_by_email(data)
    # print("This is the logged in user:", user_in_db.id)
    # Validations ---<>
    if not user_in_db:
        flash("Invalid Email/Password")
        return redirect("/")
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password")
        return redirect('/')
    session['user_id'] = user_in_db.id
    return redirect("/recipes")

### Loging Out
@app.route('/logout')
def clear_session():
    session.clear()
    print(session)
    return render_template("login.html")
