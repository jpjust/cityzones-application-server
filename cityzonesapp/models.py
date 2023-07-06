from flask_login import UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt
import os
import secrets

db = SQLAlchemy()

class PasswordsDontMatchException(Exception):
    pass

class User(UserMixin, db.Model):
    '''
    Model for users table.
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(100), unique=True, nullable=False)    
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    tasks = relationship("Task", backref='users')

    def __init__(self, email, password, password_confirmation, name, company=None):
        if password != password_confirmation:
            raise PasswordsDontMatchException
        
        self.email = email
        self.password = sha256_crypt.encrypt(password)
        self.name = name
        self.company = company

class Task(db.Model):
    '''
    Model for tasks table.
    '''
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, sqlalchemy.ForeignKey(User.id), default=1, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    base_filename = db.Column(db.String(length=64), unique=True, nullable=False)
    config = db.Column(db.JSON, nullable=False)
    geojson = db.Column(db.JSON, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    requested_at = db.Column(db.DateTime(timezone=True))
    description = db.Column(db.String(100))
    requests = db.Column(db.Integer(), nullable=False, default=0)

    result = relationship("Result", backref="task")

    def __init__(self, base_filename, config, geojson, lat, lon):
        self.base_filename = base_filename
        self.config = config
        self.geojson = geojson
        self.lat = lat
        self.lon = lon
        self.created_at = datetime.now()
        self.user_id = current_user.id
    
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
    res_data = db.Column(db.JSON)

    #task = relationship("Task", back_populates="result")

    def __init__(self, task_id):
        self.created_at = datetime.now()
        self.task_id = task_id

    def get_data(self, key):
        if self.res_data == None or not key in self.res_data.keys():
            return 0
        
        return self.res_data.get(key)

class Worker(db.Model):
    '''
    Model for workers table.
    '''
    __tablename__ = 'workers'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Unicode(200))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    tasks = db.Column(db.Integer, default=0, nullable=False)
    last_task_at = db.Column(db.DateTime)
    total_time = db.Column(db.Float, default=0.0, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.token = secrets.token_hex(32)

class CellType(db.Model):
    '''
    Model for cells_types table.
    '''
    __tablename__ = 'cells_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name

class Cell(db.Model):
    '''
    Model for cells table;
    '''
    __tablename__ = 'cells'

    id = db.Column(db.Integer, primary_key=True)
    coord = db.Column(Geometry('POINT'), nullable=False)
    radius = db.Column(db.Integer, nullable=False)
    cell_type_id = db.Column(db.Integer, sqlalchemy.ForeignKey(CellType.id))

    cell_type = relationship("CellType", backref="task")

    def __init__(self, lat, lon, radius):
        self.coord = Geometry(f'POINT("{lon} {lat}")')
        self.radius = radius
        self.cell_type_id = 1
