from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    book_title = db.Column(db.String(300))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    book_title = db.Column(db.String(300))
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(500))

class Style(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    book_title = db.Column(db.String(300))
    color = db.Column(db.String(20))
    size = db.Column(db.String(20))
    font = db.Column(db.String(50))