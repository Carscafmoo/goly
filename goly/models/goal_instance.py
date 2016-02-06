"""This package defines the goal instance class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import datetime
import json
from goly.models.user import User
from goly.models.goal import Goal
import werkzeug.local
md = MetaData(bind=db.engine)
goal = Table('goal_instance', md, autoload=True)
Base = declarative_base(metadata=md)

class GoalInstance(Base, db.Model):
    __table__ = goal_instance

    def __init__(goal, value):
        self.user = user
        self.name = name
        self.prompt = prompt
        self.frequency = frequency
        self.target = target
        self.input_type = input_type
        self.check_in_frequency = check_in_frequency
        self.active = True
        self.public = False
        self.created = datetime.datetime.now()
