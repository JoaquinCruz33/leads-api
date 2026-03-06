from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    intent = db.Column(db.String(50))
    budget = db.Column(db.Integer)
    timeline = db.Column(db.String(50))
    score = db.Column(db.Integer)
    priority = db.Column(db.String(20))