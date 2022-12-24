from flask import Blueprint, render_template

bp = Blueprint('help', __name__, url_prefix='/help')

@bp.route('/', methods=['GET'])
def index():
  '''
  Help index page.
  '''
  return render_template('help/index.html')
