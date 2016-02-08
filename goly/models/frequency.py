"""This package defines the frequency class for goly, including ORM nonsense"""
from goly import db, errors
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
md = MetaData(bind=db.engine)
frequency = Table('frequency', md, autoload=True)
Base = declarative_base(metadata=md)

class Frequency(Base, db.Model):
    __table__ = frequency

    id_cache = {}
    name_cache = {}
    cache_items = db.session.query(frequency).all()
    for cache_item in cache_items:
        id_cache[cache_item.name] = cache_item.id
        name_cache[cache_item.id] = cache_item.name
    
    def __init__(self, name):
        self.name = name

    def to_str(self):
        return self.name

    @classmethod
    def get_name_by_id(self, id):
        assert id in self.name_cache
        
        return  self.name_cache[id]

    @classmethod
    def get_id_by_name(self, name, field="Frequency"):
        assert name in self.id_cache, field + " must be one of " + ", ".join(self.id_cache.keys())
        
        return self.id_cache[name]

    @classmethod
    def conforms(self, freq, check_in_freq):
        """Determine whether a check-in frequency conforms to a frequency.

        A check-in frequency conforms to a frequency if the check-in frequency divides evenly within the 
        frequency.
        This method takes names, not IDs or objects
        """
        if (check_in_freq == freq): return True
        ## Nothing fits into daily except daily itself
        if (freq == 'daily'): return False 
        # Only days fit into weeks and months (weeks do not fit into months)
        if (freq in ['weekly', 'monthly']): return check_in_freq == 'daily' 
        if (freq == 'quarterly'): return check_in_freq in ['daily', 'monthly']
        if (freq == 'yearly'): return check_in_freq in ['daily', 'monthly', 'quarterly']

        