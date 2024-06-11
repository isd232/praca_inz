from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, FloatField, SelectField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, EqualTo
from flask_ckeditor import CKEditorField



class LocationForm(FlaskForm):
    name = StringField('Location Name', validators=[DataRequired()])
    description = CKEditorField('Location Description', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create Search location form
class TravelTipsForm(FlaskForm):
    location = StringField("Enter a location", validators=[DataRequired()])
    submit = SubmitField("Search")


# Create Fuel Calc Form
class FuelForm(FlaskForm):
    distance = FloatField('Distance in kilometers', validators=[DataRequired()])
    fuel_efficiency = FloatField('Fuel efficiency (Liters per 100 KM)', validators=[DataRequired()])
    fuel_price = FloatField('Fuel price per liter (PLN)', validators=[DataRequired()])
    submit = SubmitField('Calculate')


# Create Currency Exchange Form
class CurrencyForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    from_currency = SelectField('From', choices=[
        ('PLN', 'Polish Zloty'),
        ('EUR', 'Euro'),
        ('BAM', 'Bosnian Convertible Mark'),
        ('ALL', 'Albanian Lek'),
        ('MKD', 'Macedonian Denar'),
        ('RSD', 'Serbian Dinar'),
        ('HUF', 'Hungarian Forint')
    ], validators=[DataRequired()])
    to_currency = SelectField('To', choices=[
        ('PLN', 'Polish Zloty'),
        ('EUR', 'Euro'),
        ('BAM', 'Bosnian Convertible Mark'),
        ('ALL', 'Albanian Lek'),
        ('MKD', 'Macedonian Denar'),
        ('RSD', 'Serbian Dinar'),
        ('HUF', 'Hungarian Forint')
    ], validators=[DataRequired()])
    submit = SubmitField('Convert')


# Create Search Form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Body', validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    about_author = TextAreaField("About Author")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2',
                                                                                  message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")