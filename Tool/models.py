from flask_sqlalchemy import SQLAlchemy
from Tool import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gems = db.Column(db.Integer, default=3000)
    success_rate = db.Column(db.Float, default=0.0)
    cases_solved = db.Column(db.Integer, default=0)
    profile_pic = db.Column(db.String(255))  # Path or URL to profile picture

    def __repr__(self):
        return f"<User {self.username}>"

class Character(db.Model):
    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    image = db.Column(db.String(255))  # Path or URL to character image

    def __repr__(self):
        return f"<Character {self.name}>"

# Association table for Case and CutScene (many-to-many)
case_cutscene = db.Table('case_cutscene',
    db.Column('case_id', db.Integer, db.ForeignKey('cases.id'), primary_key=True),
    db.Column('cutscene_id', db.Integer, db.ForeignKey('cutscenes.id'), primary_key=True)
)

class CutScene(db.Model):
    __tablename__ = 'cutscenes'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))  # Path or URL to cutscene image
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)

    character = db.relationship('Character', backref=db.backref('cutscenes', lazy=True))

    def __repr__(self):
        return f"<CutScene {self.id}>"

class Case(db.Model):
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    answers = db.Column(db.Text, nullable=False)  # Can store comma-separated answers or JSON
    clues = db.Column(db.Text, nullable=False)    # Can store comma-separated clues or JSON
    cover_image = db.Column(db.String(255))  # Path or URL to cover image

    cut_scenes = db.relationship('CutScene', secondary=case_cutscene, lazy='subquery',
                                 backref=db.backref('cases', lazy=True))

    def __repr__(self):
        return f"<Case {self.id}>"
