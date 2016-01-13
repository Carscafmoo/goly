"""This package defines the user class for goly, including ORM nonsense"""
from goly import db, errors
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json
"""
@TODO: 
    - update password
    - update ... other stuff
    - get endpoint
    - email validation
    - forgot password
    - Refactor user routes into its own module
    - Update README with user docs
    - POST request validation
    - Convert all empty return values to {} so they can be json decoded
    - Test login remember me / logout?
"""
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
        if (User.pull_by_email(self.email)):
            return True

        return False

    def full_name(self):
        return self.first_name + ' ' + self.last_name

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
            raise errors.ResourceAlreadyExistsError("user", self.email)
        
        db.session.add(self)
        db.session.commit()

    def destroy(self):
        db.session.delete(self)
        db.session.commit()

    def delete(self, password):
        """Outwardly-facing method for deleting a user."""
        if self.check_password(password):
            self.destroy()
        else: raise errors.UnauthorizedError()

    def update_password(self, old_password, new_password):
        if (self.check_password(old_password)):
            self.set_password(new_password)
            if (self.exists()):
                db.session.add(self)
                db.session.flush()
                db.session.commit()

        else:
            raise errors.UnauthorizedError
            
    @classmethod
    def pull_by_id(self, id):
        return self.query.filter_by(id=id).first()

    @classmethod
    def pull_by_email(self, email):
        return self.query.filter_by(email=email).first()


