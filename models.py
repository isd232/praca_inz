from datetime import datetime
from functools import lru_cache
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# Create a Reply Model
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('Users', backref='replies')
    post = db.relationship('Posts', backref='replies')



class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))


# Create Travel Tips Model
class TravelTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    tips = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('Users', backref='travel_tips')


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
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255), nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Post {self.title} by {self.poster_id}>'

    @lru_cache(maxsize=100)
    def score(self):
        upvotes = Votes.query.filter_by(post_id=self.id, vote_type='upvote').count()
        downvotes = Votes.query.filter_by(post_id=self.id, vote_type='downvote').count()
        return upvotes - downvotes

    def user_upvoted(self, user_id):
        return Votes.query.filter_by(post_id=self.id, user_id=user_id, vote_type='upvote').count() > 0

    def user_downvoted(self, user_id):
        return Votes.query.filter_by(post_id=self.id, user_id=user_id, vote_type='downvote').count() > 0


# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    admin = db.Column(db.Boolean, default=False)
    about_author = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    # Relationship with Posts
    posts = db.relationship('Posts', backref='poster', lazy=True)  # backref provides access from Posts to Users

    def is_admin(self):
        return self.admin

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


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