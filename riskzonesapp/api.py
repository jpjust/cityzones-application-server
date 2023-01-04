from flask import Blueprint, current_app
from . import models

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/task', methods=['GET'])
def show():
    '''
    Return a task to the worker (client).
    '''
    with current_app.app_context():
        db = models.db
        task = db.session.execute(db.select(models.Task)).one()
        data = {
            'config': task[0].config,
            'geojson': task[0].geojson
        }
        return data
