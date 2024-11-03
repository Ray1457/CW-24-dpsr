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
    profile_pic = db.Column(db.String(255), default='../static/img/user/default.png')

    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    height = db.Column(db.Integer)  # Height in cm
    dob = db.Column(db.Date)
    about = db.Column(db.Text)
    
    # Relationship with clue access
    clues_accessed = db.relationship('ClueAccess', backref='user', lazy=True, cascade="all, delete-orphan")

    # Relationship with clans (this is now a many-to-many relationship)
    clans = db.relationship('Clan', secondary='room_users', backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f"<User {self.username}>"

class Case(db.Model):
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String, nullable=False)
    clues = db.Column(db.PickleType, nullable=True)          
    cover_image = db.Column(db.String(255))
    background_image = db.Column(db.String(255))
    reward = db.Column(db.Integer, default=0)
    locked = db.Column(db.Boolean, default=True)
    video = db.Column(db.String, nullable=True)
    
    # Relationship with clue access
    clues_accessed = db.relationship('ClueAccess', backref='case', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Case {self.id} - {self.title}>"

class ClueAccess(db.Model):
    __tablename__ = 'clue_access'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False)
    clue_no = db.Column(db.Integer, nullable=False)
    accessed_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<ClueAccess User {self.user_id} - Case {self.case_id} - Clue {self.clue_no}>"

class Clan(db.Model):
    __tablename__ = 'clans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    max_users = db.Column(db.Integer)
    room_code = db.Column(db.String(10), unique=True, nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    case = db.relationship('Case', backref=db.backref('rooms', lazy=True, cascade='all, delete-orphan'))
    
    # Relationships for messages
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
