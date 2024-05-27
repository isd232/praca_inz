from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from flask_migrate import Migrate
from datetime import date
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm, FuelForm, CurrencyForm
from models import Users, FuelCalculation, Posts, Votes, db
from flask_ckeditor import CKEditor
import uuid as uuid
import os
import requests


# export FLASK_ENV=development
# export FLASK_APP=app.py

# Create a Flask Instance
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)

# Add Database
# New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/users'

# Secret Key
app.config['SECRET_KEY'] = "secretkey"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize The Database
db.init_app(app)

migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

app.config['ORS_KEY'] = '5b3ce3597851110001cf624890a6fa2d528e4d4c950cbe69bd7cd863'  # Add your ORS API key here


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# Create Admin Page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 13:
        return render_template("admin.html")
    else:
        flash("Sorry you must be the Admin to access admin page...")
        return redirect(url_for('dashboard'))


# Create Search Function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the Database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()

        return render_template("search.html",
                               form=form,
                               searched=post.searched,
                               posts=posts)


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again!")
    return render_template('login.html', form=form)


# Create Logout Function
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for('login'))


# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']

        # Check for profile pic
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']
            # Grab Image Name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save That Image
            saver = request.files['profile_pic']

            # Change it to a string to save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("User Updated Successfully!")
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)
            except:
                flash("Error! Looks like there was a problem... Try again.")
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)
        else:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)
    return render_template('dashboard.html')


def get_exchange_rates():
    api_key = 'e2e106a00f79a1794cceb807'
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/PLN"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200 or data['result'] == 'error':
        raise Exception(f"API error: {data.get('error-type', 'Unknown error')}")

    return data['conversion_rates']


# Create Fuel Calculator Page
@app.route('/fuel_calculator', methods=['GET', 'POST'])
@login_required
def fuel_calculator():
    fuel_form = FuelForm()
    currency_form = CurrencyForm()
    total_cost_pln = None
    exchange_rates = None
    converted_costs = {}
    conversion_result = None

    if 'fuel_submit' in request.form and fuel_form.validate_on_submit():
        distance = fuel_form.distance.data
        fuel_efficiency = fuel_form.fuel_efficiency.data
        fuel_price = fuel_form.fuel_price.data

        total_cost_pln = (distance / 100) * fuel_efficiency * fuel_price
        flash(f'Total Fuel Cost for {distance} km: {total_cost_pln:.2f} PLN', 'fuel')

        # Save the calculation to the database
        new_calc = FuelCalculation(
            user_id=current_user.id,
            distance=distance,
            fuel_efficiency=fuel_efficiency,
            fuel_price=fuel_price,
            currency='PLN',
            total_cost=total_cost_pln
        )
        db.session.add(new_calc)
        db.session.commit()

        return redirect(url_for('fuel_calculator'))

    if 'currency_submit' in request.form and currency_form.validate_on_submit():
        amount = currency_form.amount.data
        from_currency = currency_form.from_currency.data
        to_currency = currency_form.to_currency.data

        try:
            exchange_rates = get_exchange_rates()
            if from_currency != 'PLN':
                amount_in_pln = amount / exchange_rates[from_currency]
            else:
                amount_in_pln = amount

            if to_currency != 'PLN':
                conversion_rate = exchange_rates[to_currency]
                conversion_result = round(amount_in_pln * conversion_rate, 2)
            else:
                conversion_result = round(amount_in_pln, 2)
            flash(f'{amount} {from_currency} is equal to {conversion_result} {to_currency}', 'currency')
        except Exception as e:
            flash(str(e), 'currency')

    calculations = FuelCalculation.query.filter_by(user_id=current_user.id).order_by(
        FuelCalculation.created_at.desc()).limit(5).all()
    return render_template('fuel_calculator.html', fuel_form=fuel_form, currency_form=currency_form,
                           calculations=calculations, total_cost_pln=total_cost_pln,
                           conversion_result=conversion_result)


@app.route('/map')
def map_view():
    return render_template('map.html')



@app.route('/posts/upvote/<int:id>', methods=['POST'])
@login_required
def upvote_post(id):
    post = Posts.query.get_or_404(id)
    existing_vote = Votes.query.filter_by(user_id=current_user.id, post_id=id).first()

    if existing_vote:
        if existing_vote.vote_type == 'upvote':
            db.session.delete(existing_vote)
            flash('Vote removed.', 'info')
        else:
            existing_vote.vote_type = 'upvote'
            flash('Vote changed to upvote.', 'success')
    else:
        vote = Votes(user_id=current_user.id, post_id=id, vote_type='upvote')
        db.session.add(vote)
        flash('Upvoted!', 'success')

    db.session.commit()
    return redirect(url_for('posts'))


@app.route('/posts/downvote/<int:id>', methods=['POST'])
@login_required
def downvote_post(id):
    post = Posts.query.get_or_404(id)
    existing_vote = Votes.query.filter_by(user_id=current_user.id, post_id=id).first()

    if existing_vote:
        if existing_vote.vote_type == 'downvote':
            db.session.delete(existing_vote)
            flash('Downvote removed.', 'info')
        else:
            existing_vote.vote_type = 'downvote'
            flash('Vote changed to downvote.', 'success')
    else:
        vote = Votes(user_id=current_user.id, post_id=id, vote_type='downvote')
        db.session.add(vote)
        flash('Downvoted!', 'success')

    db.session.commit()
    return redirect(url_for('posts'))


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 13:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # Return a message
            flash("Blog Post Was Deleted!")

            # Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)


        except:
            # Return an error message
            flash("Whoops! There was a problem deleting post, try again...")

            # Grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        # Return a message
        flash("You Aren't Authorized To Delete That Post!")

        # Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


@app.route('/posts')
def posts():
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted.desc()).all()
    return render_template("posts.html", posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)


# Edit Post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.poster_id or current_user.id == 13:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You Aren't Authorized To Edit This Post...")
        # Grab all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     poster_id=poster,
                     slug=form.slug.data)
        # Clear The Form
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Blog Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)


# JSON
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}


# Delete User
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    # Check logged in id vs. id to delete
    if id == current_user.id:
        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully!!")

            our_users = Users.query.order_by(Users.date_added)
            return render_template("add_user.html",
                                   form=form,
                                   name=name,
                                   our_users=our_users)

        except:
            flash("Whoops! There was a problem deleting user, try again...")
            return render_template("add_user.html",
                                   form=form, name=name, our_users=our_users)
    else:
        flash("Sorry, you can't delete that user! ")
        return redirect(url_for('dashboard'))


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
        except:
            flash("Error! Looks like there was a problem... Try again.")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
    else:
        return render_template("update.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


# Add User
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash password
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            user = Users(username=form.username.data,
                         name=form.name.data,
                         email=form.email.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users)


# Create a route decorator
@app.route('/')
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


# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form
        form.email.data = ''
        form.password_hash.data = ''

        # Lookup User By Email Address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)


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


# Check if the executed file is the main program and not a module imported elsewhere
if __name__ == '__main__':
    # Set Flask configuration to development mode explicitly
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    app.run()
