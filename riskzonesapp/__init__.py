from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask
from . import models, map, about, help

def create_app(test_config=None):
    '''
    Create the RiskZones Web Flask App.
    '''
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URI'),
    )
    models.db.init_app(app)

    with app.app_context():
        models.db.create_all()

    # Blueprints
    app.register_blueprint(map.bp)
    app.register_blueprint(about.bp)
    app.register_blueprint(help.bp)

    app.config.from_pyfile('config.py', silent=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def index():
        return map.show()

    return app
