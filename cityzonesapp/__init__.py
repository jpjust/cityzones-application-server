"""
CityZones Application Server module
Copyright (C) 2023 João Paulo Just Peixoto

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*******************************************************************************

This module runs the CityZones Application Server as a Flask application.
"""

from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask
from flask_alembic import Alembic
from flask_login import LoginManager
from . import models, auth, api, map, worker, about, help

def create_app(test_config=None):
    '''
    Create the CityZones Web Flask App.
    '''
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URI'),
    )
    models.db.init_app(app)
    alembic = Alembic()
    alembic.init_app(app)

    # Auth
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return models.User.query.get(int(user_id))

    # Create results directories
    try:
        os.makedirs(str(os.getenv('RESULTS_DIR')))
    except FileExistsError:
        pass

    # Blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(map.bp)
    app.register_blueprint(about.bp)
    app.register_blueprint(help.bp)
    app.register_blueprint(worker.bp)

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
