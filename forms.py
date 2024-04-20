from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class UserCreateForm(FlaskForm):
    """Form for creating users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class LaunchListForm(FlaskForm):
    """Form for making a list of launches"""

    name = StringField('Name', validators=[DataRequired])
    launch = StringField('Launch')