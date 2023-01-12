from flask import Blueprint, Response, current_app, request
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from . import models
import os
import io
import json
import secrets

bp = Blueprint('api', __name__, url_prefix='/api')
db = models.db

@bp.before_request
def authorize():
    if secrets.compare_digest(str(request.headers.get('X-API-Key')), os.getenv("API_KEY")) == False:
        return Response(json.dumps({'msg': 'Unauthorized.'}), headers={'Content-type': 'application/json'}, status=401)

@bp.route('/task', methods=['GET'])
def get_task():
    '''
    Return a task to the worker (client).
    '''
    with current_app.app_context():
        request_exp = datetime.now() - timedelta(minutes=int(os.getenv('TASK_REQ_EXP')))
        max_requests = int(os.getenv('TASK_REQ_MAX'))
        tasks = db.session.query(models.Task).where(and_(models.Task.requests < max_requests, or_(models.Task.requested_at < request_exp, models.Task.requested_at == None))).all()

        for task in tasks:
            if len(task.result) == 0:
                task.requested_at = datetime.now()
                task.requests += 1
                db.session.commit()

                data = {
                    'id': task.id,
                    'config': task.config,
                    'geojson': task.geojson
                }
                return data

    return Response(json.dumps({'msg': 'No tasks to perform.'}), headers={'Content-type': 'application/json'}, status=204)

@bp.route('/result/<int:id>', methods=['POST'])
def post_result(id):
    '''
    Receive a result from the worker and save its data.
    '''
    try:
        with current_app.app_context():
            task = db.get_or_404(models.Task, id)

            # Check if there is a result for this task
            if len(task.result) > 0:
                return Response(json.dumps({'msg': 'There is a result for this task already.'}), headers={'Content-type': 'application/json'}, status=409)
            
            # Read stream
            fp = None
            boundary = request.stream.readline().strip()

            while True:
                line = request.stream.readline()

                # If there is no data, stream is over
                if len(line) == 0:
                    if fp != None: fp.close()
                    result = models.Result(task.id)
                    models.db.session.add(result)
                    models.db.session.commit()
                    return Response(json.dumps({'msg': 'Data received succesfully.'}), headers={'Content-type': 'application/json'}, status=201)

                # If line is blank, the file contents is about to begin
                if line == b'\r\n':
                    while True:
                        line = request.stream.readline()

                        # Check if the contents of the file has ended
                        if line.startswith(boundary):
                            if fp == None or fp.closed: break

                            fp.seek(-1, io.SEEK_CUR)
                            fp.truncate()
                            fp.close()
                            break

                        if fp != None and not fp.closed:
                            fp.write(line.strip())
                            fp.write(b'\n')

                # Other case is a line of headers
                else:
                    if b'name="map"' in line:
                        if fp != None: fp.close()
                        fp = open(f'{os.getenv("RESULTS_DIR")}/{task.base_filename}_map.csv', 'wb')
                    elif b'name="edus"' in line:
                        if fp != None: fp.close()
                        fp = open(f'{os.getenv("RESULTS_DIR")}/{task.base_filename}_edus.csv', 'wb')
                    elif b'name="roads"' in line:
                        if fp != None: fp.close()
                        fp = open(f'{os.getenv("RESULTS_DIR")}/{task.base_filename}_roads.csv', 'wb')

    except KeyError:
        return Response(json.dumps({'msg': 'Received data is incomplete.'}), headers={'Content-type': 'application/json'}, status=400)
