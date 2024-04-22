from flask import Flask, render_template


# export FLASK_ENV=development
# export FLASK_APP=app.py
# Create a Flask Instance
app = Flask(__name__)


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
    return  render_template("404.html")


# Invalid URL
@app.errorhandler(500)
def page_not_found(e):
    return  render_template("500.html")