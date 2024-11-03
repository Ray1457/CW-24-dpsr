from flask_sqlalchemy import SQLAlchemy
from Tool import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    gems = db.Column(db.Integer, default=3000)
    success_rate = db.Column(db.Float, default=0.0)
    cases_solved = db.Column(db.Integer, default=0)
    profile_pic = db.Column(db.String(255), default='../static/img/user/default.png')  # Path or URL to profile picture
    # New fields for additional profile info
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    height = db.Column(db.Integer)  # Height in cm
    dob = db.Column(db.Date)
    about = db.Column(db.Text)

    def __repr__(self):
        return f"<User {self.username}>"


class Case(db.Model):
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # Title for the case/chapter
    description = db.Column(db.Text, nullable=False)    # Detailed description or storyline
    answer = db.Column(db.String, nullable=False)        # Storing answers (JSON or comma-separated)
    clues = db.Column(db.PickleType, nullable=True)          
    cover_image = db.Column(db.String(255))             # Path or URL to cover image
    background_image = db.Column(db.String(255))        # Background image for the case/chapter
    reward = db.Column(db.Integer, default=0)      # Points or rewards for completion
    locked = db.Column(db.Boolean, default=True)        # Indicates if the case is locked or unlocked
    video = db.Column(db.String, nullable = True)

    def __repr__(self):
        return f"<Case {self.id} - {self.title}>"



class Clan(db.Model):
    __tablename__ = 'clans'
    id = db.Column(db.Integer, primary_key=True)
    name = room_code = db.Column(db.String, unique=True, nullable=False)
    max_users = db.Column(db.Integer)
    room_code = db.Column(db.String(10), unique=True, nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    case = db.relationship('Case', backref=db.backref('rooms', lazy=True, cascade='all, delete-orphan'))
    
    # Cascade delete the association with users and messages when a clan is deleted
    users = db.relationship('User', secondary='room_users', backref=db.backref('rooms', lazy='dynamic'), cascade="all, delete")
    messages = db.relationship('Message', backref='room', lazy=True, cascade="all, delete-orphan")

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    room_id = db.Column(db.Integer, db.ForeignKey('clans.id', ondelete='CASCADE'))

    # Relationships
    user = db.relationship('User', backref=db.backref('messages', lazy=True, cascade='all, delete-orphan'))


# Association table for users in rooms
room_users = db.Table('room_users',
    db.Column('room_id', db.Integer, db.ForeignKey('clans.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)


