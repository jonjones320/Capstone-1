import os

from flask import Flask, render_template, redirect, session, g, flash, url_for, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import bcrypt, check_password_hash
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Launch, Collection, Launch_Collection, SQLAlchemy
from forms import RegisterUserForm, CollectionForm, LaunchForm, ProfileForm, LoginForm
from helpers import previous_launches, all_launches, get_launch, launch_search

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
            return redirect("/launch/index")

        flash("Invalid credentials.", 'danger')
    
    return render_template('/user/login.html', form=form, current_user=g.user)
    

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

        flash("Account created succesfully. Welcome!", "success")
        return redirect(url_for('show_all_launches'))

    else: return render_template('/user/register.html', form=form)


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

    user = User.query.get_or_404(user_id)

    collection = (Collection
                .query
                .filter(Collection.createdBy == user_id)
                .order_by(Collection.createdDate.desc())
                .limit(100)
                .all())
    
    return render_template('user/profile.html', user=user, collections=collection)


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
        try:
            if User.authenticate(user.username, form.password.data):
                User.edit_profile(
                    user,
                    username=form.username.data or user.username,
                    email=user.email or form.email.data,
                    img_url=form.img_url.data or user.img_url,
                    header_img_url=form.header_img_url.data or user.header_img_url,
                    bio=form.bio.data 
                        or user.bio,
                    location=form.location.data 
                        or user.location
                    )
                flash("Profile updated!", "success")
                return redirect(f'{user_id}')
            else:
                flash("Incorrect password", "danger")
                return render_template('user/edit.html', form=form, user=user)

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('user/edit.html', form=form, user=user)
    else:
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
        try:
            collection = Collection.create(
                name=form.name.data,
                description=form.description.data,
                img_url=form.img_url.data,
                createdBy=g.user.id
                )
            db.session.commit()

        except IntegrityError:
            flash('Name is already taken', 'danger')
            return render_template('collection/new.html', form=form)
        
        flash(f"{collection.name} created succesfully. Start collecting now!", 'success')
        return redirect(url_for('collection_show', collection_id=collection.id))
    
    return render_template('collection/new.html', form=form)


@app.route('/collection/user/<int:user_id>')
def all_collections(user_id):
    """Shows all of a user's collections"""

    user = User.query.get_or_404(user_id)

    return render_template('collection/all.html', user=user)


@app.route('/collection/<int:collection_id>')
def collection_show(collection_id):
    """Show a collection."""

    collection = Collection.query.get(collection_id)
    user = User.query.get(collection.createdBy)
    launch_collections = Launch_Collection.query.filter_by(collectionID=collection_id).all()
    launch_ids = [each.launchID for each in launch_collections]

    launches = []
    for launch_id in launch_ids:
        launch = Launch.query.filter_by(id=launch_id).first()
        launches.append(launch)

    return render_template('collection/view.html', collection=collection, user=user, launches=launches)

@app.route('/collection/edit/<int:collection_id>', methods=["GET", "POST"])
def collection_edit(collection_id):
    """Edit a collection."""

    collection = Collection.query.get(collection_id)
    user = User.query.get(collection.createdBy)
    launch_collections = Launch_Collection.query.filter_by(collectionID=collection_id).all()
    launch_ids = [each.launchID for each in launch_collections]

    launches = []
    for launch_id in launch_ids:
        launch = Launch.query.filter_by(id=launch_id).first()
        launches.append(launch)

    form = CollectionForm()
    
    if user is g.user:
        if form.validate_on_submit():
            try:
                Collection.edit_collection(
                    name=form.data.name,
                    img_url=form.data.img_url,
                    description=form.data.description
                    )    
                flash("Collection updated!", "success")
                return redirect(f'{collection.id}')

            except IntegrityError:
                flash("Username already taken", 'danger')
                return render_template('collection/view.html', form=form, user=user, launches=launches)
    else:
        return render_template('collection/view.html', collection=collection, user=user, launches=launches)


@app.route('/collection/<int:collection_id>/delete', methods=["POST"])
def collection_delete(collection_id):
    """Delete a collection."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    Collection.query.filter_by(id=collection_id).delete()

    db.session.commit()

    return redirect(url_for("all_collections", user_id=g.user.id))


#################################### Launch ##########################################

@app.route('/launch/search')
def search_launches():
    """Searches launches"""

    search_term = request.args.get('q')
    
    if not search_term:
        flash("")
        return redirect('/launch/index')
    else:
        searched_launches = launch_search(search_term)

    if searched_launches is None:
        flash("No results found. Try again, or browse the launches below", "danger")
        return redirect('/launch/index')
    else:
        return render_template('launch/index.html', launches=searched_launches, current_user=g.user)
    

@app.route('/launch/index')
def show_all_launches():
    """Displays all launches"""
    
    launches = all_launches()
    collections = Collection.query.filter_by(createdBy=g.user.id).all()

    return render_template('launch/index.html', launches=launches, current_user=g.user, collections=collections)


@app.route('/launch/<launch_name>')
def view_launch(launch_name):
    """View a launch"""

    launch_data = get_launch(launch_name)
    collections = Collection.query.filter_by(createdBy=g.user.id).all()

    return render_template('launch/view.html', launch_data=launch_data, collections=collections)


@app.route('/launch/collect/<launch_name>/<int:collection_id>', methods=['POST'])
def collect_launch(launch_name, collection_id):
    """Adds a launch to a collection"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    launch = get_launch(launch_name)
    print("-------get_launch: ", launch, "----------")
    existing_launch = Launch.query.filter_by(name=launch[0]['Name']).first()
    print("-------existing_launch: ", existing_launch, "----------")
    if not existing_launch:
        new_launch = Launch(launch)
        print("-------new_launch: ", new_launch, "----------")
        launch_id = new_launch.id
        db.session.add(new_launch)
        db.session.commit()
    else:
        launch_id = existing_launch.id
    
    try:
        collection = Collection.query.filter_by(id=collection_id).first()
        print("---------collection: ", collection, "---------")
        if collection:
            launch_collection = Launch_Collection(collectionID=collection_id, launchID=launch_id)
            print("--------launch_collection: ", launch_collection, "--------")
            db.session.add(launch_collection)
            db.session.commit()
    except IntegrityError:
        flash("Launch already exists in this collection", "danger")
        return redirect(url_for('view_launch', launch_name=launch_name))

    flash("Launch collection successful!", "success")
    return redirect(url_for('view_launch', launch_name=launch_name))


@app.route('/launch/uncollect/<int:launch_id>', methods=['POST'])
def uncollect(launch_id):
    """Removes selected launch from current user's collection."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    launch = get_launch(launch_id)
    collected_launch = Launch.query.get(launch_id)
    g.user.collection.remove(collected_launch)
    db.session.commit()

    return redirect(url_for('view_launch', launch_name=launch.name))



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