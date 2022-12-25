from dotenv import load_dotenv
load_dotenv()

import os

from flask import Flask
from . import map, about, help

def create_app(test_config=None):
  '''
  Create the RiskZones Web Flask App.
  '''
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'riskzonesapp.sqlite'),
  )

  # Blueprints
  app.register_blueprint(map.bp)
  app.register_blueprint(about.bp)
  app.register_blueprint(help.bp)

  if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
  else:
    # load the test config if passed in
    app.config.from_mapping(test_config)

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
