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
class RegisterUserForm(ModelForm):
    """Form for creating users."""
    class Meta:
        model = User
    # username = StringField(
    #         'Username', validators=[DataRequired()])
    # email = EmailField(
    #         'E-mail', validators=[DataRequired(), Email()])
    # image_url = StringField( 
    #         'Image URL')
    # header_image_url = StringField( 
    #         'Header Image URL')
    # bio = StringField(
    #         "Bio")
    # location = StringField(
    #         "Location")
        password = PasswordField(
            'Password', validators=[DataRequired(), Length(min=6)])
    # confirmPassword = PasswordField(
    #         'Confirm Password', validators=[DataRequired(), EqualTo("password", message="Passwords do not match.")])

    # VS Code provided validation. Checks the form entries vs. the validators:
    def validate(self, extra_validators: Mapping[str, Sequence[Any]] | None = None) -> bool:
        return super().validate(extra_validators)


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

    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[Email()])
    password = StringField('Password', validators=[DataRequired()])


class ProfileForm(ModelForm):
    """Form for creating and editing a user profile"""

    username = StringField(
            'Username', validators=[DataRequired()])
    image_url = StringField( 
            'Image URL')
    header_image_url = StringField( 
            'Header Image URL')
    bio = StringField(
            "Bio")
    location = StringField(
            "Location")
    password = PasswordField(
            'Password', validators=[DataRequired()])
    