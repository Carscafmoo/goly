"""This package defines the user class for goly, including ORM nonsense"""
from goly import db, errors
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
import datetime
import json
"""
@TODO: 
    - forgot password
    - Test login remember me / logout?
"""
md = MetaData(bind=db.engine)
user = Table('user', md, autoload=True)
Base = declarative_base(metadata=md)

class User(Base, db.Model):
    __table__ = user
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
        if (not self.id):
            self.id = self.pull_by_email(self.email).get_id()

        return self.id

    def exists(self):
        if (User.pull_by_email(self.email)):
            return True

        return False

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def set_password(self, password):
        self.password = generate_password_hash(password, salt_length=32)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email, 
            "first_name": self.first_name, 
            "last_name": self.last_name,
            "registered_on": str(self.registered_on)
            }

    def to_json(self):
        return json.dumps(self.to_dict())

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

    def update_email(self, new_email, password):
        if (not self.check_password(password)):
            raise errors.UnauthorizedError    
        
        if User.pull_by_email(new_email):
            raise ResourceAlreadyExistsError("user", new_email)
        
        self.email = new_email
        if (self.exists()):
            db.session.add(self)
            db.session.flush()
            db.session.commit()

    def update(self, data):
        fields = set(['first_name', 'last_name']) & set(data.keys())
        for key in fields:
            setattr(self, key, data[key])

        if (self.exists()):
            db.session.add(self)
            db.session.flush()
            db.session.commit()

    @classmethod
    def pull(self, params):
        count = params['count'] if 'count' in params else 20
        offset = params['offset'] if 'offset' in params else 0
        sort  = params['sort'] if 'sort' in params and params['sort'] in ['id', 'email', 'first_name', 'last_name', 'registered_on'] else 'email'
        sort_order = params['sort_order'] if 'sort_order' in params else 'asc'

        order_by = getattr(self, sort)
        if (sort_order == 'desc'): order_by = order_by.desc()
        
        return self.query.order_by(order_by).limit(count).offset(offset).all()

            
    @classmethod
    def pull_by_id(self, id):
        return self.query.filter_by(id=id).first()

    @classmethod
    def pull_by_email(self, email):
        return self.query.filter_by(email=email).first()


