"""SQLAlchemy models for the Launch Tracker."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

bcrypt = Bcrypt()

db = SQLAlchemy()


class User(db.Model):
    """User details"""

    __tablename__ = 'users'

    id = db.Column( 
        db.Integer, primary_key=True)

    username = db.Column(
        db.Text, nullable=False, unique=True)

    email = db.Column(
        db.Text, nullable=False, unique=True)

    password = db.Column(
        db.Text, nullable=False)

    bio = db.Column(
        db.Text, nullable=True)

    location = db.Column( 
        db.Text, nullable=True)

    created_on = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now())

    img_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png")
    
    header_img_url = db.Column(
        db.Text,
        default="/static/images/spaceX_launch_streak_201603.avif")
    
    active = db.Column(
        db.Boolean, nullable=False, default=True)
    

    def is_collected(user_id, launch_id):
        """Checks if a user has a launch in their collections"""
        try: 
            user = User.query.get_or_404(user_id)
            launch = Launch.query.get_or_404(launch_id)
        except:
            print("User or Launch not found")
            return False
        
        for collection in user.collections:
            if launch in collection.launches:
                return True
        return False
    
    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"


    @classmethod
    def register(cls, username, email, password, bio, location, img_url, header_img_url):
        """Sign up user. Hashes password and adds user to database"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            bio=bio,
            location=location,
            img_url=img_url,
            header_img_url=header_img_url
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def edit_profile(cls, user, username, email, image_url, header_image_url, bio, location):
        """Edits and updates user profile."""

        user.username=username,
        user.email=email,
        user.image_url=image_url,
        user.header_image_url=header_image_url,
        user.bio=bio,
        user.location=location
        print("---Before user commit---")
        db.session.commit()
        print("--- User committed ---")
        return User()



class Launch(db.Model):
    """Launch information"""

    __tablename__ = 'launches' 

    id = db.Column(
        db.Integer,
        primary_key=True
        )
    name = db.Column(
        db.Text, 
        nullable=False, 
        unique=True
        )
    date = db.Column(db.Text)
    location = db.Column(db.Text)
    pad = db.Column(db.Text)

    def __repr__(self):
        return f"<Launch #{self.id}: {self.name}, on {self.date}, at {self.location}, {self.pad}>"





class Launch_Collection(db.Model):
    """Join table for Launch and Collection"""

    __tablename__ = 'launch_collections'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    collectionID = db.Column(
        db.ForeignKey('collections.id', ondelete='CASCADE'),
        nullable=False
    )
    launchID = db.Column(
        db.ForeignKey('launches.id', ondelete='CASCADE'),
        nullable=False
    )


class Collection(db.Model):
    """A collection of launches"""

    __tablename__ = 'collections'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    name = db.Column(
        db.String,
        nullable=False
    )
    description = db.Column(
        db.String,
        nullable=True,
    )
    createdDate = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now()
    )
    createdBy = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User', backref='collections')

    launches = db.relationship(
        "Launch",
        secondary="launch_collections",
        backref="collections",
        primaryjoin=("Collection.id == Launch_Collection.collectionID"),
        secondaryjoin=("Launch.id == Launch_Collection.launchID"),
        lazy="dynamic"
    )


def connect_db(app):
    """Connect this database to provided Flask app.
        Sets the context for the app.    
    """

    db.app = app
    db.init_app(app)
    app_ctx = app.app_context()
    app_ctx.push()
    db.create_all()
