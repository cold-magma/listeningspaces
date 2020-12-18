from . import db
from flask_login import UserMixin

class User(db.Model,UserMixin):
    email_id = db.Column(db.String(100), primary_key=True, unique=True)
    password = db.Column(db.String(100))
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    token_time = db.Column(db.Integer)
    name = db.Column(db.String(100))
    room_key = db.Column(db.String(100))
    last_auth_date = db.Column(db.String(100))
    last_auth_time = db.Column(db.String(100))

    def get_id(self):
        return self.email_id

class Room(db.Model):
    room_key = db.Column(db.String(100), primary_key=True)
    owner = db.Column(db.String(100))
    connected_users = db.Column(db.Integer)
    