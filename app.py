import os

from flask import Flask, render_template, redirect, session, g, flash, url_for, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import bcrypt, check_password_hash
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Launch, Collection, Launch_Collection, SQLAlchemy
from forms import RegisterUserForm, CollectionForm, LaunchForm, ProfileForm, LoginForm
from helpers import previous_launches, all_launches, get_launch

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


######################################## Login Setup ###################################################

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

@app.context_processor
def inject_getattr():
    return dict(getattr=getattr)


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
            flash(f"Hello, {form.username.data}!", "success")
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
            flash('Username is already taken', 'danger')
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


@app.route('/user/profile/<int:user_id>')
def view_user(user_id):
    """View a user's profile."""

    collections = (Collection
                .query
                .filter(Collection.createdBy == user_id)
                .order_by(Collection.createdDate.desc())
                .limit(100)
                .all())
    
    return render_template('user/profile.html', user=g.user, collections=collections)


@app.route('/user/profile/edit', methods=["GET", "POST"])
def profile():
    """Handle profile editing."""

    form = ProfileForm()
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id = g.user.id
    user = User.query.get_or_404(user_id)
            
    if form.validate_on_submit():
        print("---1:valid on submit ---")
        try:
            if User.authenticate(user.username, form.password.data):
                print("---2:user authenticated ---")
                User.edit_profile(
                    user,
                    username=user.username or form.username.data,
                    email=user.email or form.email.data,
                    image_url=form.img_url.data or user.img_url,
                    header_image_url=form.header_img_url.data or user.header_img_url,
                    bio=form.bio.data 
                        or user.bio,
                    location=form.location.data 
                        or user.location
                    )
                print("---3:edit_profile ran ---")
                flash("Profile updated!", "success")
                return redirect(f'{user_id}')
            else:
                print("---4: Not authenticated ---")
                flash("Incorrect password", "danger")
                return render_template('user/edit.html', form=form, user=user)

        except IntegrityError:
            print("---5: Integrity Error ---")
            flash("Username already taken", 'danger')
            return render_template('user/edit.html', form=form, user=user)
    else:
        print("---6: Not valid on submit ---")
        return render_template('user/edit.html', form=form, user=user)


@app.route('/user/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/register")

#################################### Collection Routes ####################################

@app.route('/collection/new', methods=["GET", "POST"])
def collections_new():
    """Create a new collection"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = CollectionForm()

    if form.validate_on_submit():
        description = Collection(description=form.description.data)
        db.session.commit()

        return redirect(f"/launch/index")

    return render_template('collection/new.html', form=form)


@app.route('/collection/<int:user_id>')
def all_collections(user_id):
    """Shows all of a user's collections"""

    user = User.query.get_or_404(user_id)

    return render_template('collection/all.html', user=user)


@app.route('/collection/<int:collection_id>', methods=["GET", "POST"])
def collection_show(collection_id):
    """Show or edit a specific collection."""

    collection = Collection.query.get(collection_id)
    return render_template('collection/show.html', collection=collection)


@app.route('collection/collect/<int:launch_id>', methods=["POST"])
def collect_launch(launch_id):
    """Add a launch to a collection."""

    if not g.user:
        flash("You must be logged in to use that feature.", "danger")
        return redirect("/login")
    
    user = User.query.get(g.user.id)

    return redirect('collection/all.html', user=g.user)


@app.route('/collection/<int:collections_id>/delete', methods=["POST"])
def collection_delete(collection_id):
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
def search_launches():
    """Searches launches"""
    search = request.args.get('q')

    allLaunches = all_launches()

    searched_launches = [
        launch for launch in allLaunches if search.lower() in launch['name'].lower()]

    return render_template('launch/index.html', launches=searched_launches)
    

@app.route('/launch/index')
def show_all_launches():
    """Displays all launches"""
    
    launches = all_launches()

    if g.user:
        user = User.query.get(g.user.id)

    return render_template('launch/index.html', launches=launches)


@app.route('/user/collect/<int:launch_id>', methods=['POST'])
def collect_launch(launch_id, collection_id):
    """Adds a launch to the collection"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    launch = get_launch(launch_id)
    collection = Collection.query.get_or_404(collection_id)
    collection.launches.append(launch)
    db.session.commit()

    return redirect("launch/index")


@app.route('/user/uncollect/<int:launch_id>', methods=['POST'])
def uncollect(launch_id):
    """Removes selected launch from current user's collection."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    collected_launch = Launch.query.get(launch_id)
    g.user.collection.remove(collected_launch)
    db.session.commit()

    return redirect(f"/launch/index")



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