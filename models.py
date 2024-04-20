"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User details"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    bio = db.Column(
        db.Text,
        nullable=True
    )
    
    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    location = db.Column(
        db.Text,
        nullable=True
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )


    collections = db.relationship(
        "User",
        secondary="collections"
    )

    favorites = db.relationship(
        "User",
        secondary="favorites"
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"



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
        unique=True,
    )

    date = db.Column(
        db.Text,
    )
    
    location = db.Column(
        db.Text,
    )

    pad = db.Column(
        db.Text,
    )

    def __repr__(self):
        return f"<Launch #{self.id}: {self.name}, on {self.date}, at {self.location}, {self.pad}>"



class Collection(db.Model):
    """A collection of launches"""

    __tablename__ = 'collections'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    launch_id = db.Column(
        db.Integer,
        db.ForeignKey('launches.id', ondelete='CASCADE')
    )

    description = db.Column(
        db.String,
        nullable=True,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now()
    )

    user = db.relationship('User')



class Favorite(db.Model):
    """Favorite collections"""

    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    launch_id = db.Column(
        db.Integer,
        db.ForeignKey('launches.id', ondelete='CASCADE'),
        nullable=False,
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
