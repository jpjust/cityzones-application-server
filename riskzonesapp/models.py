from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import os

db = SQLAlchemy()

class Task(db.Model):
    '''
    Model for tasks table.
    '''
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    base_filename = db.Column(db.String(length=64), nullable=False)
    config = db.Column(db.JSON, nullable=False)
    geojson = db.Column(db.JSON, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    requested_at = db.Column(db.DateTime(timezone=True), nullable=True)
    description = db.Column(db.String(100), nullable=True)
    requests = db.Column(db.Integer, nullable=False, default=0)

    result = relationship("Result", back_populates="task")

    def __init__(self, base_filename, config, geojson, lat, lon):
        self.base_filename = base_filename
        self.config = config
        self.geojson = geojson
        self.lat = lat
        self.lon = lon
        self.created_at = datetime.now()
    
    def expired(self):
        if self.requested_at == None:
            return False

        request_exp = datetime.now() - timedelta(minutes=int(os.getenv('TASK_REQ_EXP')))
        return self.requested_at < request_exp
    
    def failed(self):
        return self.expired() and self.requests >= int(os.getenv('TASK_REQ_MAX'))
    
    def task_data(self):
        data = {
            'zl': self.config['zone_size'],
            'pois': {}
        }

        pois_types = self.config['pois_types']
        for poi in pois_types['amenity'].keys():
            data['pois'][poi] = pois_types['amenity'][poi]['w']
        
        for poi in pois_types['railway'].keys():
            data['pois'][poi] = pois_types['railway'][poi]['w']

        return data
        
class Result(db.Model):
    '''
    Model for results table.
    '''
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    task_id = db.Column(db.Integer, sqlalchemy.ForeignKey(Task.id))

    task = relationship("Task", back_populates="result")

    def __init__(self, task_id):
        self.created_at = datetime.now()
        self.task_id = task_id
