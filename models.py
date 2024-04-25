"""SQLAlchemy models for the Launch Tracker."""

from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

bcrypt = Bcrypt()

db = SQLAlchemy()


class User(UserMixin, db.Model):
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
        db.DateTime, nullable=True)

    img_url = db.Column(
        db.Text,
        default="/static/images/default_img.avif")
    
    header_img_url = db.Column(
        db.Text,
        default="/static/images/spaceX_launch_streak_201603.avif")
    
    active = db.Column(
        db.Boolean, nullable=False, default=True)


    @classmethod
    def edit_profile(cls, user, username, email, image_url, header_image_url, bio, location):
        """Edits and updates user profile."""

        user.username=username,
        user.email=email,
        user.image_url=image_url,
        user.header_image_url=header_image_url,
        user.bio=bio,
        user.location=location

        db.session.commit()

    def __init__(self, email, username, password, bio, location, img_url, header_img_url):
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.bio = bio 
        self.location = location 
        self.created_on = datetime.now()
        self.img_url = img_url
        self.header_img_url = header_img_url

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"



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
