"""This package defines the user class for goly, including ORM nonsense"""
from goly import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json

class User(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    email = db.Column('email', db.String(50), nullable=False, unique=True, index=True)
    first_name = db.Column('first_name', db.String(50))
    last_name = db.Column('last_name', db.String(50))
    password = db.Column('password', db.String(50))
    registered_on = db.Column('registered_on', db.DateTime)    

    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.set_password(password)
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

    def exists(self):
        if (self.query.filter_by(email=self.email)).first():
            return True

        return False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_json(self):
        return json.dumps({
            "id": self.id,
            "email": self.email, 
            "first_name": self.first_name, 
            "last_name": self.last_name,
            "registered_on": str(self.registered_on)
            })

    def persist(self):
        if (self.exists()):
            raise DuplicateEntryError(self.email)
        
        db.session.add(self)
        db.session.commit()
        
class DuplicateEntryError(Exception):
    def __init__(self, entry):
        self.entry = entry
