from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user, AnonymousUserMixin
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, ValidationError, \
    SelectMultipleField, widgets, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired
from buddyWheels.models import User

