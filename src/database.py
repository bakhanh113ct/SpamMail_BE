from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random
import json
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    # emails = db.relationship('Email', backref='user', lazy='dynamic')

    def __repr__(self) -> str:
        return 'User>>> {self.username}'


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    body = db.Column(db.Text(), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])
    is_spam = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def toJSON(self):
        print(self.__dict__)
        return json.dumps(self)

    def __repr__(self) -> str:
        return 'Email>>> {self.url}'


# class Bookmark(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text, nullable=True)
#     url = db.Column(db.Text, nullable=False)
#     short_url = db.Column(db.String(3), nullable=True)
#     visits = db.Column(db.Integer, default=0)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     created_at = db.Column(db.DateTime, default=datetime.now())
#     updated_at = db.Column(db.DateTime, onupdate=datetime.now())

#     def generate_short_characters(self):
#         characters = string.digits+string.ascii_letters
#         picked_chars = ''.join(random.choices(characters, k=3))

#         link = self.query.filter_by(short_url=picked_chars).first()

#         if link:
#             self.generate_short_characters()
#         else:
#             return picked_chars

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#         self.short_url = self.generate_short_characters()

#     def __repr__(self) -> str:
#         return 'Boomark>>> {self.url}'
