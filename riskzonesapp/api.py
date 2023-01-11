from flask import Blueprint, Response, current_app, request, send_file, stream_with_context
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from zipfile import ZipFile, ZIP_DEFLATED
from . import models
import os
import io
import json
import csv

bp = Blueprint('api', __name__, url_prefix='/api')
db = models.db

@bp.route('/task', methods=['GET'])
def get_task():
    '''
    Return a task to the worker (client).
    '''
    with current_app.app_context():
        request_exp = datetime.now() - timedelta(minutes=int(os.getenv('TASK_REQ_EXP')))
        tasks = db.session.query(models.Task).where(or_(models.Task.requested_at < request_exp, models.Task.requested_at == None)).all()

        for task in tasks:
            if len(task.result) == 0:
                task.requested_at = datetime.now()
                db.session.commit()

                data = {
                    'id': task.id,
                    'config': task.config,
                    'geojson': task.geojson
                }
                return data

    return Response(json.dumps({'msg': 'No tasks to perform.'}), headers={'Content-type': 'application/json'}, status=204)

@bp.route('/result/<int:id>', methods=['GET'])
def get_result(id):
    '''
    Get a result by its ID and respond with its map data.
    '''
    with current_app.app_context():
        result = db.session.query(models.Result).where(models.Result.task_id == id).first()

        if result == None:
            return Response(json.dumps({'msg': 'There is no result for this task yet.'}), headers={'Content-type': 'application/json'}, status=404)

        map_file = f'{os.getenv("RESULTS_DIR")}/{result.task.base_filename}_map.csv'
        edus_file = f'{os.getenv("RESULTS_DIR")}/{result.task.base_filename}_edus.csv'
        classification = {
            'center_lat': 0,
            'center_lon': 0,
            'zl': result.task.config['zone_size'],
            '1': [],
            '2': [],
            '3': [],
            'edus': []
        }

        left = 180
        right = -180
        bottom = 90
        top = -90

        try:
            # Classification data
            fp = open(map_file, 'r')
            reader = csv.reader(fp)
            fp.readline()  # Skip header line

            for row in reader:
                M = row[1]
                geodata = json.loads(row[2])
                coord = geodata['coordinates']
                classification[M].append(coord)
                if coord[0] < left:   left   = coord[0]
                if coord[0] > right:  right  = coord[0]
                if coord[1] < bottom: bottom = coord[1]
                if coord[1] > top:    top    = coord[1]

            fp.close()

            classification['center_lat'] = (bottom + top) / 2
            classification['center_lon'] = (left + right) / 2

            # EDUs data
            fp = open(edus_file, 'r')
            reader = csv.reader(fp)
            fp.readline()  # Skip header line

            for row in reader:
                geodata = json.loads(row[1])
                coord = geodata['coordinates']
                classification['edus'].append(coord)

            fp.close()

            return classification
        except FileNotFoundError:
            return Response(json.dumps({'msg': 'Results file not found for this task.'}), headers={'Content-type': 'application/json'}, status=500)

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
                            fp.seek(-1, io.SEEK_CUR)
                            fp.truncate()
                            fp.close()
                            break
                        
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

    except KeyError:
        return Response(json.dumps({'msg': 'Received data is incomplete.'}), headers={'Content-type': 'application/json'}, status=400)

@bp.route('/result/download/<int:id>', methods=['GET'])
def download_result(id):
    '''
    Get a result by its ID and respond with its CSV files in ZIP format.
    '''
    with current_app.app_context():
        result = db.session.query(models.Result).where(models.Result.task_id == id).first()

        if result == None:
            return Response(json.dumps({'msg': 'There is no result for this task yet.'}), headers={'Content-type': 'application/json'}, status=404)

        map_file = f'{os.getenv("RESULTS_DIR")}/{result.task.base_filename}_map.csv'
        edus_file = f'{os.getenv("RESULTS_DIR")}/{result.task.base_filename}_edus.csv'
        zip_data = io.BytesIO()

        with ZipFile(zip_data, 'w', compression=ZIP_DEFLATED, compresslevel=9) as myzip:
            myzip.write(map_file, arcname=f'{result.task.base_filename}_map.csv')
            myzip.write(edus_file, arcname=f'{result.task.base_filename}_edus.csv')
        
        zip_data.seek(0)
        return send_file(
            zip_data,
            as_attachment=True,
            download_name=f'{result.task.base_filename}.zip',
            mimetype='application/zip'
        )
