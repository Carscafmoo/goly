"""This package defines the user class for goly, including ORM nonsense"""
from goly import db
import datetime

class User(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    email = db.Column('email', db.String(50), nullable=False, unique=True, index=True)
    first_name = db.Column('first_name', db.String(50))
    last_name = db.Column('last_name', db.String(50))
    password = db.Column('password', db.String(50))
    registered_on = db.Column('registered_on', db.DateTime)    

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.registered_on = datetime.datetime.utcnow()

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)

    def persist(self):
        db.session.add(self)
        db.session.commit()
    
