from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func, case
from sqlalchemy.orm import column_property

db = SQLAlchemy()


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))


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

    @hybrid_property
    def score(self):
        # Placeholder for Python side; real logic in @score.expression
        return 0

    @score.expression
    def score(cls):
        upvotes = select([func.count()]).where(Votes.post_id == cls.id, Votes.vote_type == 'upvote').label(
            'upvotes').as_scalar()
        downvotes = select([func.count()]).where(Votes.post_id == cls.id, Votes.vote_type == 'downvote').label(
            'downvotes').as_scalar()
        return upvotes - downvotes


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
    posts = db.relationship('Posts', backref='poster', lazy='dynamic')
    votes = db.relationship('Votes', backref='voter', lazy='dynamic')
    
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
