from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterUserForm(FlaskForm):
    """Form for creating users."""

    username = StringField(
            'Username', 
            validators=[DataRequired()])
    email = EmailField(
            'E-mail', 
            validators=[DataRequired(), Email()])
    image_url = StringField( 
            '(Optional) Image URL')
    password = PasswordField(
            'Password', 
            validators=[DataRequired, Length(min=6)])
    confirmPassword = PasswordField(
            'Confirm Password', 
            validators=[DataRequired, EqualTo("password", message="Passwords do not match.")])

    # VS Code provided validation. Checks the form entries vs. the validators:
    def validate(self, extra_validators: Mapping[str, Sequence[Any]] | None = None) -> bool:
        return super().validate(extra_validators)



class LoginForm(FlaskForm):
    """Login user form"""

    username = StringField('Username', validators=[DataRequired])
    email = EmailField('Email', validators=[Email])
    password = StringField('Password', validators=[DataRequired])



class LaunchListForm(FlaskForm):
    """Form for making a list of launches"""

    name = StringField('Name', validators=[DataRequired])
    launch = StringField('Launch')


