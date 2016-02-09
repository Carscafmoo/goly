"""This package defines the goal instance class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import datetime
import json
from goly.models.user import User
from goly.models.goal import Goal
from goly.models.timeframe import Timeframe
from 
import werkzeug.local
md = MetaData(bind=db.engine)
goal = Table('check_in', md, autoload=True)
Base = declarative_base(metadata=md)

class CheckIn(Base, db.Model):
    __table__ = goal_instance

    def __init__(goal, timeframe, value):
        self.goal = goal 
        self.timeframe = timeframe ## have to do something about this, yeah?
        self.value = value

    @validates('goal')
    def validate_goal(self, key, goal):
        assert isinstance(goal, Goal), "Passed goal must be a goal object!"
        self.goal_obj = goal

        return goal.get_id()

    @validates('timeframe')
    def validate_timeframe(self, key, timeframe):
        assert isinstance(timeframe, Timeframe)
        assert timeframe.frequency == self.goal_obj.check_in_frequency
        self.timeframe_obj = timeframe

        return timeframe.get_id()
    
    @orm.reconstructor
    def reconstruct(self):
        self.goal_obj = Goal.pull_by_id(self.goal)
        self.timeframe_obj = Timeframe.pull_by_id(self.timeframe)


    @validates('value'):
    def validate_value(self, key, value):
        ## Confirm that value conforms to goal type (e.g., binary is boolean, numeric is a number)
