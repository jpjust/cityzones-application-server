from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask
from flask_alembic import Alembic
from . import models, api, map, about, help

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
    alembic = Alembic()
    alembic.init_app(app)

    # Create database tables
    with app.app_context():
        models.db.create_all()

    # Create results directories
    try:
        os.makedirs(os.getenv('RESULTS_DIR'))
    except FileExistsError:
        pass

    # Blueprints
    app.register_blueprint(api.bp)
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
