"""This package defines the goal class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import datetime
import json
from goly.models.user import User
import werkzeug.local
"""
@TODO: Test
@TODO: Add pretty much all functionality
@TODO: Add prompt

"""
md = MetaData(bind=db.engine)
goal = Table('goal', md, autoload=True)
Base = declarative_base(metadata=md)

class Goal(Base, db.Model):
    __table__ = goal

    def __init__(self, user, name, prompt, frequency, target, input_type):
        self.user = user
        self.name = name
        self.prompt = prompt
        self.frequency = frequency
        self.target = target
        self.input_type = input_type
        self.active = True
        self.public = False
        self.created = datetime.datetime.now()


    def get_id(self):
        if (not self.id):
            self.id = self.pull_by_name(self.user, self.name).get_id()

        return self.id

    @validates("user")
    def validate_user(self, key, user):
        ## current_user is an instance of werkzeug.local.LocalProxy apparently ?
        assert isinstance(user, User) or isinstance(user, werkzeug.local.LocalProxy), "user must be a User!"
        assert user.exists(), "Passed user does not exist"

        return user.get_id()

    @validates("name")
    def validate_name(self, key, name):
        name = name.strip()
        length = len(name)
        assert length > 0 and length <= 50, "Name must be between 0 and 50 characters"

        return name

    @validates("prompt")
    def validate_prompt(self, key, prompt):
        prompt = prompt.strip()
        length = len(prompt)
        assert length > 0 and length <= 255, "Prompt must be between 0 and 255 characters"

        return prompt

    @validates("frequency")
    def validate_frequency(self, key, freq):
        freq = freq.strip()
        assert freq in ['daily', 'weekly', 'monthly', 'quarterly', 'yearly'], "Frequency must be one of daily, weekly, monthly, quarterly, or even yearly"

        return freq

    @validates("target")
    def validate_target(self, key, target):
        assert isinstance(target, (int, long)) or (isinstance(target, (str, unicode)) and target.isdigit()), "Target must be an integer"

        return target

    @validates("input_type")
    def validate_input_type(self, key, it):
        assert it in ['binary', 'numeric'], "Input type must be binary or numeric"

        return it

    @validates("active")
    def validate_active(self, key, active):
        assert isinstance(active, bool), "Active must be a boolean"

        return active

    @validates("public")
    def validate_public(self, key, public):
        assert isinstance(public, bool), "Public must be a boolean"

        return public

    def to_dict(self):
        return { 
            "id": self.get_id(),
            "user": self.user,
            "name": self.name,
            "prompt": self.prompt,
            "frequency": self.frequency,
            "target": self.target,
            "input_type": self.input_type,
            "active": self.active,
            "public": self.public,
            "created": str(self.created)
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def persist(self):
        if (self.exists()):
            raise errors.ResourceAlreadyExistsError("goal", self.name)
        
        db.session.add(self)
        db.session.commit()

    def exists(self):
        if (Goal.pull_by_name(self.user, self.name)):
            return True

        return False

    def destroy(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, data):
        fields = set(['name', 'prompt', 'frequency', 'target', 'input_type', 'active', 'public']) & set(data.keys())
        for key in fields:
            if (key == 'name'):
                if (self.pull_by_name(self.user, data[key])):
                    raise ResourceAlreadyExistsError("goal", self.name)

            setattr(self, key, data[key])

        if (self.exists()):
            db.session.add(self)
            db.session.flush()
            db.session.commit()

    def pull(self, params):
        return self.pull_by_user(self.user, params, False)

    @classmethod 
    def pull_by_user(self, user, params, public_only=True):
        count = params['count'] if 'count' in params else 20
        offset = params['offset'] if 'offset' in params else 0
        sort  = params['sort'] if 'sort' in params and params['sort'] in ['id', 'created', 'name', 'frequency'] else 'name'
        sort_order = params['sort_order'] if 'sort_order' in params else 'asc'

        order_by = getattr(self, sort)
        if (sort_order == 'desc'): order_by = order_by.desc()

        if (public_only):
            return self.query.filter_by(public=True).order_by(order_by).limit(count).offset(offset).all()
        
        return self.query.order_by(order_by).limit(count).offset(offset).all()

    @classmethod
    def pull_by_id(self, id):
        return self.query.filter_by(id=id).first()

    @classmethod
    def pull_by_name(self, user, name):
        return self.query.filter_by(user=user).filter_by(name=name).first()

    @classmethod
    def delete(self, user, id):
        goal = self.query.filter_by(id=id).first()
        if (not goal): 
            raise errors.NotFoundError()

        if (user != goal.user):
            raise errors.UnauthorizedError()
    
        goal.destroy() ## Should raise something if the goal doesn't exist
        

    

