"""This package defines the goal class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import datetime
import json
from goly.models.user import User
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

    def __init__(self, user, name, frequency, target, input_type):
        self.user = user
        self.name = name
        self.frequency = frequency
        self.target = target
        self.input_type = input_type
        self.active = True
        self.public = False
        self.created = datetime.datetime.now()

    @validates("user")
    def validate_user(self, key, user):
        assert isinstance(user, User), "user must be a User!"
        assert user.exists(), "Passed user does not exist"

    @validates("name")
    def validate_name(self, key, name):
        length = len(name)
        assert length > 0 and length <= 50, "Name must be between 0 and 50 characters"

    @validates("frequency")
    def validate_target(self, key, freq):
        assert freq in ['day', 'week', 'month', 'quarter', 'year'], "Frequency must be one of day, week month, quarter, or even year"

    @validates("target")
    def validate_frequency(self, key, target):
        assert isinstance(target, (int, long)) or (isinstance(target, str) and freq.isdigit()), "Target must be an integer"

    @validates("input_type")
    def validate_input_type(self, key, it):
        assert it in ['binary', 'numeric'], "input_type must be binary or numeric"

    @validates("active")
    def validate_active(self, key, active):
        assert isinstance(active, bool), "active must be a boolean"

    @validates("public")
    def validate_public(self, key, public):
        assert isinstance(public, bool), "public must be a boolean"


    

