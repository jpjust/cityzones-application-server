from flask import Blueprint, render_template, request
from . import meta

bp = Blueprint('map', __name__, url_prefix='/map')

@bp.route('/show', methods=['GET'])
def show():
  '''
  Map index page.
  '''
  return render_template('map/index.html')

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

    if poi_hospital: conf['pois_types']['amenity'].append('hospital')
    if poi_firedept: conf['pois_types']['amenity'].append('fire_station')
    if poi_police:   conf['pois_types']['amenity'].append('police')

    meta.write_conf(f"{base_filename}.json", conf, geojson)

    return render_template('map/index.html', info_msg='Your request was successfully queued.')

  except KeyError:
    return render_template('map/index.html', error_msg='Error: all fields are mandatory.')
  except IndexError:
    return render_template('map/index.html', error_msg='There was an error trying to parse the AoI polygon. Check if you created a valid AoI before submitting a map request.')