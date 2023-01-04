from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

    def __init__(self, base_filename, config, geojson):
        self.base_filename = base_filename
        self.config = config
        self.geojson = geojson
        self.created_at = datetime.now()
