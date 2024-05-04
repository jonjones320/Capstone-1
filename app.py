import os

from flask import Flask, render_template, redirect, session, g, flash, url_for, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import bcrypt, check_password_hash
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Launch, Collection, Launch_Collection, SQLAlchemy
from forms import RegisterUserForm, CollectionForm, LaunchForm, ProfileForm, LoginForm
from helpers import previous_launches, all_launches

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///launch_tracker'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "It's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


######################################## Login Manager Setup ###################################################

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    
    flash("You have been logged out.", "success")


#################################  Register/login/logout routes ############################################# 

@app.route('/login', methods=['GET','POST'])
def login():
    """Logs in user"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {g.user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')
    
    return render_template('/user/login.html', form=form, current_user=g.user)


@app.route('/register', methods=["GET","POST"])
def register():

    form = RegisterUserForm()
    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                email=form.email.data, 
                password=form.password.data,
                bio=form.bio.data,
                location=form.location.data,
                img_url=form.img_url.data or User.img_url.default.arg,
                header_img_url=form.header_img_url.data or User.header_img_url.default.arg
            )
            db.session.commit()
        except IntegrityError:
            print(str(IntegrityError.orig))
            flash(f'{str(IntegrityError.orig)}', 'danger')
            return render_template('user/register.html', form=form)
        
        do_login(user)

        flash("Account created succesfully. Welcome!")
        return redirect(url_for('homepage'))

    else: return render_template('/user/register.html', form=form)
    
@app.route('/logout')
def logout():
    """Log out user"""

    try:
        do_logout()

    except IntegrityError:
        flash("You have been logged out.", "success")
        return redirect("/user")
    
    return redirect(url_for("homepage"))


#################################  General User routes #############################################



@app.route('/user/index')
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


@app.route('/user/<int:user_id>')
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
    
    return render_template('user/collections.html', user=g.user, collections=collections)


@app.route('/user/profile', methods=["GET", "POST"])
def profile():
    """Handle profile editing."""

    form = ProfileForm()
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id = g.user.id
    user = User.query.get_or_404(user_id)
            
    if form.validate_on_submit():
        try:
            if User.authenticate(user.username, form.password.data):

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
                return render_template('user/edit.html', form=form)

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('user/edit.html', form=form)
    else:
        return render_template('user/edit.html', form=form)


@app.route('/user/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

#################################### Collection Routes ####################################

@app.route('/collections/new', methods=["GET", "POST"])

def collections_add():
    """Create a new collection"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = CollectionForm()

    if form.validate_on_submit():
        description = Collection(description=form.description.data)
        db.session.commit()

        return redirect(f"/user/{g.user.id}")

    return render_template('collection/new.html', form=form)


@app.route('/collections/<int:collection_id>', methods=["GET", "POST"])
def collection_show(collection_id):
    """Show or edit a collection."""

    collection = Collection.query.get(collection_id)
    return render_template('collections/show.html', collection=collection)


@app.route('/messages/<int:user_id>/liked')
def favorite_collection_show(user_id):
    """Show a users favorite collection."""

    user_id = g.user.id
    fave_collection = []
    fave_collection_id = [favorite.collection_id for favorite in Collection.query.filter_by(user_id=user_id).all()]

    for collection_id in fave_collection_id:
        new_collection = Collection.query.get(collection_id)
        fave_collection.append(new_collection)

    return render_template('messages/liked.html', fave_collection=fave_collection)


@app.route('/collections/<int:collections_id>/delete', methods=["POST"])
def collections_destroy(collection_id):
    """Delete a collection."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    collection = Collection.query.get(collection_id)
    db.session.delete(collection)
    db.session.commit()

    return redirect(f"/user/{g.user.id}")

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
    if g.user:

        return render_template('home.html', launches=launches, current_user=g.user)
    
    # Display all launches, without future logged-in user personalization.
    else:
        return render_template('home-anon.html', launches=launches, current_user=g.user)