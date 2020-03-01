from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flask_clustering.auth import login_required
from flask_clustering.db import get_db

bp = Blueprint('file', __name__, url_prefix='/file')

@bp.route('/')
def index():
    db = get_db()
    files = db.execute(
        'SELECT f.id, f.name, f.path, f.created, f.uploaded, username, user_id FROM file f JOIN user u'
        ' ON f.user_id = u.id ORDER BY created, uploaded DESC'
    ).fetchall()
    return render_template('file/index.html', files=files)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        path = request.form['path']
        error = None

        if not path:
            error = 'File Path is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO file (user_id, path, name)'
                ' VALUES (?, ?, ?)',
                (g.user['id'], path, 'filename')
            )
            db.commit()
            return redirect(url_for('file.index'))
    return render_template('file/create.html')

def get_file(id, check_author=True):
    file = get_db().execute(
        'SELECT f.id, path, created, user_id, username'
        ' FROM file f JOIN user u ON f.user_id = u.id'
        ' WHERE f.id = ?', (id,)).fetchone()

    if file is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and file['user_id'] != g.user['id']:
        abort(403)

    return file

@bp.route('/<int:id>/update', methods=('GET','POST'))
@login_required
def update(id):
    file = get_file(id)

    if request.method == 'POST':
        path = request.form['path']
        error = None

        if not path:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE file SET path = ?'
                ' WHERE id = ?',
                (path, id)
            )
            db.commit()
            return redirect(url_for('file.index'))

    return render_template('file/update.html', file=file)

@bp.route('/<int:id>/delete', methods=('POST', ))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM file WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('file.index'))
