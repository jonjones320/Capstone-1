import os

from flask import Flask, render_template, redirect, session, flash, url_for
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import bcrypt, check_password_hash

from models import db, connect_db, User, Launch, Collection, Launch_Collection
from forms import LoginForm, RegisterUserForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///launch_tracker'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "It's a secret")
login_manager = LoginManager()
toolbar = DebugToolbarExtension(app)

connect_db(app)

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    
    if User.get(user_id):
        return User.get(user_id)
    else: return None

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.is_authenticated(form.username.data,
                                     form.password.data)
        if user:
            login_user(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')
        return redirect(url_for(login), form=form)
    
    return render_template('login.html', form=form)


@app.route('/register', methods=["GET","POST"])
def register():

    form = RegisterUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data, 
            password=form.password.data,
            img_url=form.img_url.data,
            header_img_url=form.header_img_url.data
            )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created succesfully. Welcome!")

        return redirect(url_for('home'))
    
@app.route('logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))