import os

from flask import Flask, render_template, redirect, session, flash, url_for, request, jsonify
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import bcrypt, check_password_hash
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Launch, Collection, Launch_Collection, SQLAlchemy
from forms import RegisterUserForm, CollectionForm, LaunchForm, ProfileForm, LoginForm
from helpers import previous_launches, all_launches

app = Flask(__name__)
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///launch_tracker'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "It's a secret")
login_manager = LoginManager()
toolbar = DebugToolbarExtension(app)

connect_db(app)


######################################## Login Manager Setup ###################################################

login_manager.init_app(app)

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(email):
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user = User()
    user.id = email
    return user


#################################  Register/login/logout routes ############################################# 

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    users = User.query.get().all()
    if form.validate_on_submit():
        email = request.form['email']
        if email in users and request.form['password'] == users[email]['password']:
            login_user()
            flash(f"Hello, {current_user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')
        return redirect(url_for('login'), form=form)
    
    return render_template('/user/login.html', form=form)


@app.route('/register', methods=["GET","POST"])
def register():

    form = RegisterUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data, 
            password=form.password.data,
            bio=form.bio.data,
            location=form.location.data,
            img_url=form.img_url.data,
            header_img_url=form.header_img_url.data
            )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created succesfully. Welcome!")

        return redirect(url_for('/'))
    else: return render_template('/user/register.html', form=form)
    
@app.route('/logout')
@login_required
def logout():
    # user = User.is_authenticated(current_user.username,
    #                                  current_user.password)
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("homepage"))


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

    return render_template('user/index.html', users=users)


@app.route('/users/<int:user_id>')
def view_user(user_id):
    """View a user's profile."""

        # collections = []

        # for collection in collections:
        #         collection = (Collection
        #                     .query
        #                     .filter_by(current_user.id)
        #                     .order_by(Collection.createdDate.desc())
        #                     .limit(100)
        #                     .first())
        #         collections.append(collection)

    # retrieving a user's collections, sorted by when it was made
    collections = (Collection
                .query
                .filter(Collection.createdBy == user_id)
                .order_by(Collection.createdDate.desc())
                .limit(100)
                .all())
    
    return render_template('user/collections.html', user=current_user, collections=collections)


@app.route('/users/profile', methods=["GET", "POST"])
@login_required
def profile():
    """Handle profile editing."""

    form = ProfileForm()
    
    user_id = current_user.id

# validates the edit form
    if form.validate_on_submit():
        try:
            
# ensures the user entered correct password to edit that specific profile 
            if User.is_authenticated(form.username.data,
                                     form.password.data):

# uses @classmethod 'edit_profile' to update profile
# or uses previous user data
                User.edit_profile(
                    current_user,
                    username=form.username.data 
                        or current_user.username,
                    email=form.email.data 
                        or current_user.email,
                    image_url=form.image_url.data 
                        or User.image_url.default.arg or current_user.image_url,
                    header_image_url=form.header_image_url.data 
                        or User.header_image_url.default.arg or current_user.header_image_url,
                    bio=form.bio.data 
                        or current_user.bio,
                    location=form.location.data 
                        or current_user.location
                    )

                flash("Profile updated!", "success")
                return redirect(f'{user_id}')
            else:
                flash("Incorrect password", "danger")
                return render_template('user/edit.html', form=form)

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/edit.html', form=form)
    else:
        return render_template('user/edit.html', form=form)


@app.route('/users/delete', methods=["POST"])
@login_required
def delete_user():
    """Delete user."""

    if not current_user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    logout_user()

    db.session.delete(current_user)
    db.session.commit()

    return redirect("/signup")

#################################### Collection Routes ####################################

@app.route('/collections/new', methods=["GET", "POST"])
@login_required
def collections_add():
    """Create a new collection"""

    if not current_user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = CollectionForm()

    if form.validate_on_submit():
        description = Collection(description=form.description.data)
        current_user.append(description)
        db.session.commit()

        return redirect(f"/users/{current_user.id}")

    return render_template('collection/new.html', form=form)


@app.route('/collections/<int:collection_id>', methods=["GET", "POST"])
def collection_show(collection_id):
    """Show or edit a collection."""

    collection = Collection.query.get(collection_id)
    return render_template('collections/show.html', collection=collection)


@app.route('/messages/<int:user_id>/liked')
def favorite_collection_show(user_id):
    """Show a users favorite collection."""

    user_id = current_user.id
    fave_collection = []
    fave_collection_id = [favorite.collection_id for favorite in Collection.query.filter_by(user_id=user_id).all()]

    for collection_id in fave_collection_id:
        new_collection = Collection.query.get(collection_id)
        fave_collection.append(new_collection)

    return render_template('messages/liked.html', fave_collection=fave_collection)


@app.route('/collections/<int:collections_id>/delete', methods=["POST"])
@login_required
def collections_destroy(collection_id):
    """Delete a collection."""

    if not current_user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    collection = Collection.query.get(collection_id)
    db.session.delete(collection)
    db.session.commit()

    return redirect(f"/users/{current_user.id}")

#################################### Launch ##########################################

@app.route('/launch/search')
def show_launches():
    """Searches launches"""
    search = request.args.get('q')

    allLaunches = all_launches()

    searched_launches = [
        launch for launch in allLaunches if search.lower() in launch['name'].lower()]

    return render_template('launch/index.html', launches=searched_launches)
    



#################################### Homepage ##########################################

@app.route('/')
def homepage():
    """Show homepage:
        Displays all launches.
        If logged in, displays additional user information.
    """

    launches = all_launches()

    # Display all launches. 
    # Future addition: customize launches/favorites/collections if authenticated.
    if current_user.id is not None:

        return render_template('home.html', launches=launches, current_user=current_user)
    
    # Display all launches, without future logged-in user personalization.
    else:
        return render_template('home-anon.html', launches=launches, current_user=current_user)