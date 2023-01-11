from flask import Blueprint, current_app, render_template, request
from . import meta, models

bp = Blueprint('map', __name__, url_prefix='/map')
db = models.db

DEFAULT_MAP_LON = -8.596
DEFAULT_MAP_LAT = 41.178

@bp.route('/show', methods=['GET'])
def show():
    '''
    Map index page.

    Shows the map centered on FEUP.
    '''
    return render_template('map/index.html', lon=DEFAULT_MAP_LON, lat=DEFAULT_MAP_LAT)

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
        edus         = int(request.form['edus'])
        edu_alg      = request.form['edu_alg']

        poi_hospital = ('poi_hospital' in request.form.keys())
        poi_firedept = ('poi_firedept' in request.form.keys())
        poi_police   = ('poi_police'   in request.form.keys())
        poi_metro    = ('poi_metro'    in request.form.keys())

        w_hospital   = float(request.form['w_hospital']) if poi_hospital else 0
        w_firedept   = float(request.form['w_firedept']) if poi_firedept else 0
        w_police     = float(request.form['w_police'])   if poi_police   else 0
        w_metro      = float(request.form['w_metro'])    if poi_metro    else 0

        polygon      = eval(request.form['polygon'])

        if len(polygon) < 3:
            return render_template('map/index.html', error_msg='At least 3 points are required for an AoI polygon.', lon=DEFAULT_MAP_LON, lat=DEFAULT_MAP_LAT)

        # Generate configuration files
        geojson = meta.make_polygon(polygon)
        base_filename, conf = meta.make_config_file(polygon, zl, edus, edu_alg)
        center_lon = (conf['left'] + conf['right']) /2
        center_lat = (conf['bottom'] + conf['top']) /2

        if poi_hospital: conf['pois_types']['amenity']['hospital'] = {'w': w_hospital}
        if poi_firedept: conf['pois_types']['amenity']['fire_station'] = {'w': w_firedept}
        if poi_police:   conf['pois_types']['amenity']['police'] = {'w': w_police}
        if poi_metro:    conf['pois_types']['railway']['station'] = {'w': w_metro}

        # Store in database        
        with current_app.app_context():
            task = models.Task(base_filename, conf, geojson, center_lat, center_lon)
            models.db.session.add(task)
            models.db.session.commit()

            return render_template('map/index.html', info_msg=f'Your request was successfully queued. Request number: {task.id}.', lat=center_lat, lon=center_lon)

    except KeyError:
        return render_template('map/index.html', error_msg='Error: all fields are mandatory.', lon=DEFAULT_MAP_LON, lat=DEFAULT_MAP_LAT)
    except IndexError:
        return render_template('map/index.html', error_msg='There was an error trying to parse the AoI polygon. Check if you created a valid AoI before submitting a map request.', lon=DEFAULT_MAP_LON, lat=DEFAULT_MAP_LAT)
    except ValueError:
        return render_template('map/index.html', error_msg='There was an error trying to parse some parameters. Check if you entered proper values.', lon=DEFAULT_MAP_LON, lat=DEFAULT_MAP_LAT)

@bp.route('/results', methods=['GET'])
def results():
    '''
    Results index page.

    Shows the results of previous requests to display on map.
    '''
    with current_app.app_context():
        tasks = db.session.query(models.Task).all()
        return render_template('map/results.html', tasks=tasks)
