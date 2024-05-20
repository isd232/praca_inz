from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# Create a Votes Model
class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    vote_type = db.Column(db.String(10))  # 'upvote' or 'downvote'

    user = db.relationship('Users', backref=db.backref('votes', lazy='dynamic'))
    post = db.relationship('Posts', backref=db.backref('votes', lazy='dynamic'))


# Create a Blog Post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign Key To Link Users (refer to primary key to the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def score(self):
        upvotes = Votes.query.filter_by(post_id=self.id, vote_type='upvote').count()
        downvotes = Votes.query.filter_by(post_id=self.id, vote_type='downvote').count()
        return upvotes - downvotes


# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(500), nullable=True)
    # Password Hashing
    password_hash = db.Column(db.String(128))
    # User Can Have Many Posts
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name


# Create Fuel Consumption Model
class FuelCalculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    fuel_efficiency = db.Column(db.Float, nullable=False)
    fuel_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FuelCalculation {self.distance} km, {self.fuel_efficiency} L/100km, {self.fuel_price} {self.currency}>'
