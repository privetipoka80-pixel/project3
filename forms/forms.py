from wtforms import Form, StringField, PasswordField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange
import re

class RegistrationForm(Form):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ProductForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    category = StringField('Category', validators=[Length(max=100)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
