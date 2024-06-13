from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms_alchemy import model_form_factory
from models import db, User, Collection, Launch

######## Model Form Factory Setup ###########
BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


########### Forms from Database Models #############
class RegisterUserForm(FlaskForm):
        """Form for creating users."""

        username = StringField(
            'Username', validators=[DataRequired()])
        email = EmailField(
            'E-mail', validators=[DataRequired(), Email()])
        img_url = StringField( 
            'Image URL')
        header_img_url = StringField( 
            'Header Image URL')
        bio = StringField(
            "Bio")
        location = StringField(
            "Location")
        password = PasswordField(
            'Password', validators=[DataRequired(), Length(min=6)])
        confirmPassword = PasswordField(
            'Confirm Password', validators=[DataRequired(), 
            EqualTo("password", message="Passwords do not match.")])



class CollectionForm(ModelForm):
    """Form for creating and editing a collection"""
    class Meta:
        model = Collection


class LaunchForm(ModelForm):
    """Form for making a list of launches"""
    class Meta:
        model = Launch



################# App Functionality Forms ###################

class LoginForm(FlaskForm):
    """Login user form"""

    username = StringField(
        'Username', validators=[DataRequired()])
    email = EmailField(
        'Email', validators=[Email()])
    password = PasswordField(
        'Password', validators=[DataRequired()])


class ProfileForm(ModelForm):
    """Form for creating and editing a user profile"""

    username = StringField(
            'username', validators=[DataRequired()])
    img_url = StringField( 
            'img_url')
    header_img_url = StringField( 
            'header_img_url')
    bio = StringField(
            "bio")
    location = StringField(
            "location")
    password = PasswordField(
            'password', validators=[DataRequired()])
    