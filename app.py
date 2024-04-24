import os

from flask import Flask, render_template, redirect, session, flash, url_for, request
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import bcrypt, check_password_hash
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Launch, Collection, Launch_Collection
from forms import LoginForm, RegisterUserForm, ProfileForm

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


######################################## Flask Login Manager Setup ###################################################

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    
    if User.get(user_id):
        return User.get(user_id)
    else: return None


#################################  Register/login/logout routes ############################################# 

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
        return redirect(url_for('login'), form=form)
    
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
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


#################################  General User routes #############################################



@app.route('/users')
def list_users():
    """Lists all users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def view_user(user_id):
    """View a user's profile."""

    user = User.query.get_or_404(user_id)

    # retrieving a user's collections, sorted by when it was made
    collections = (Collection
                .query
                .filter(Collection.createdBy == user_id)
                .order_by(Collection.createdDate.desc())
                .limit(100)
                .all())
    
    return render_template('users/show.html', user=user, collections=collections)


@app.route('/users/profile', methods=["GET", "POST"])
@login_required
def profile():
    """Handle profile editing."""

    form = ProfileForm()
    
    user_id = current_user.id
    user = User.query.get_or_404(user_id)

# validates the edit form
    if form.validate_on_submit():
        try:
            
# ensures the user entered correct password to edit that specific profile 
            if User.is_authenticated(form.username.data,
                                     form.password.data):

# uses @classmethod 'edit_profile' to update profile
# or uses previous user data
                User.edit_profile(
                    user,
                    username=form.username.data 
                        or user.username,
                    email=form.email.data 
                        or user.email,
                    image_url=form.image_url.data 
                        or User.image_url.default.arg or user.image_url,
                    header_image_url=form.header_image_url.data 
                        or User.header_image_url.default.arg or user.header_image_url,
                    bio=form.bio.data 
                        or user.bio,
                    location=form.location.data 
                        or user.location
                    )

                flash("Profile updated!", "success")
                return redirect(f'{user_id}')
            else:
                flash("Incorrect password", "danger")
                return render_template('users/edit.html', form=form)

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/edit.html', form=form)
    else:
        return render_template('users/edit.html', form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not current_user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    logout_user(current_user)

    db.session.delete(current_user)
    db.session.commit()

    return redirect("/signup")

