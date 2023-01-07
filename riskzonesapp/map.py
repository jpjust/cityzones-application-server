from flask import Blueprint, current_app, render_template, request
from . import meta, models

bp = Blueprint('map', __name__, url_prefix='/map')
db = models.db

@bp.route('/show', methods=['GET'])
def show():
    '''
    Map index page.

    Shows the map centered on FEUP.
    '''
    return render_template('map/index.html', lat='-8.596', lon='41.178')

@bp.route('/run', methods=['POST'])
def run():
    '''
    Map request method.

    This method will create the task files and write them to the queue folder.
    A background app will be responsible to check new tasks and execute them.
    '''
    try:
        # Form data
        zl           = int(request.form['zl'])
        poi_hospital = ('poi_hospital' in request.form.keys())
        poi_firedept = ('poi_firedept' in request.form.keys())
        poi_police   = ('poi_police'   in request.form.keys())
        polygon      = eval(request.form['polygon'])

        # Generate configuration files
        geojson = meta.make_polygon(polygon)
        base_filename, conf = meta.make_config_file(polygon, zl)
        center_lon = (conf['left'] + conf['right']) /2
        center_lat = (conf['bottom'] + conf['top']) /2

        if poi_hospital: conf['pois_types']['amenity'].append('hospital')
        if poi_firedept: conf['pois_types']['amenity'].append('fire_station')
        if poi_police:   conf['pois_types']['amenity'].append('police')

        # Store in database        
        with current_app.app_context():
            task = models.Task(base_filename, conf, geojson, center_lat, center_lon)
            models.db.session.add(task)
            models.db.session.commit()

            return render_template('map/index.html', info_msg=f'Your request was successfully queued. Request number: {task.id}.', lat=polygon[0][0], lon=polygon[0][1])

    except KeyError:
        return render_template('map/index.html', error_msg='Error: all fields are mandatory.')
    except IndexError:
        return render_template('map/index.html', error_msg='There was an error trying to parse the AoI polygon. Check if you created a valid AoI before submitting a map request.')
    except ValueError:
        return render_template('map/index.html', error_msg='There was an error trying to parse some parameters. Check if you entered proper values.')

@bp.route('/results', methods=['GET'])
def results():
    '''
    Results index page.

    Shows the results of previous requests to display on map.
    '''
    with current_app.app_context():
        tasks = db.session.query(models.Task).all()
        return render_template('map/results.html', tasks=tasks)
