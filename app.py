from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# export FLASK_ENV=development
# export FLASK_APP=app.py


# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "nothing for now"


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a route decorator
@app.route('/')
# def index():
#     return "<h1>Hello world!</h1>"

def index():
    first_name = "John"
    return render_template("index.html", first_name=first_name)


# localhost:5000/user/john
@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name=name)


# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


# Invalid URL
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html")


# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")

    return render_template("name.html",
                           name=name,
                           form=form)
