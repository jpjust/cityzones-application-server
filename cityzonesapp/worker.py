from flask import Blueprint, redirect, render_template, request
from flask_login import login_required, current_user
from . import models

bp = Blueprint('worker', __name__, url_prefix='/worker')
db = models.db

@bp.before_request
def authorize():
    if current_user.id != 1:
        return redirect('/')

@bp.route('/list', methods=['GET'])
@login_required
def list(info_msg=None, error_msg=None):
    '''
    Workers listing page.

    Shows the workers and buttons to handle them.
    '''
    return render_template('worker/index.html', workers=models.Worker.query.all(), info_msg=info_msg, error_msg=error_msg)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    '''
    Workers add page.

    Shows a form to register a new worker.
    '''
    if request.method == 'GET':
        return render_template('worker/form.html')
    
    elif request.method == 'POST':
        worker = models.Worker(request.form['name'], request.form['description'])
        models.db.session.add(worker)
        models.db.session.commit()
        return list(info_msg=f'Worker "{worker.name}" added.')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    '''
    Workers edit page.

    Shows a form to edit a worker.
    '''
    worker = models.Worker.query.get(id)
    if worker == None:
        return list(error_msg='Worker does not exist.')

    if request.method == 'GET':
        return render_template('worker/form.html', worker=worker)

    elif request.method == 'POST':
        worker.name = request.form['name']
        worker.description = request.form['description']
        models.db.session.add(worker)
        models.db.session.commit()
        return list(info_msg=f'Worker "{worker.name}" edited.')

@bp.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    '''
    Deletes a worker from the database.
    '''
    worker = models.Worker.query.get(id)
    if worker == None:
        return list(error_msg='Worker does not exist.')

    models.db.session.delete(worker)
    models.db.session.commit()
    return list(info_msg=f'Worker "{worker.name}" deleted.')
