import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flask_clustering.auth import login_required
from flask_clustering.db import get_db

from . import cluster

bp = Blueprint('file', __name__, url_prefix='/file')

@bp.route('/')
@login_required
def index():
    db = get_db()
    files = db.execute(
        'SELECT f.id, f.name, f.path, f.created, f.uploaded, username, user_id FROM file f JOIN user u'
        ' ON f.user_id = u.id and u.id = '+str(g.user['id'])+' ORDER BY f.uploaded DESC'
    ).fetchall()
    return render_template('file/index.html', files=files)

@bp.route('/<int:file_id>')
def file_detail(file_id):
    db = get_db()
    file = db.execute(
        'SELECT f.id, f.name, f.path, f.created, f.uploaded, username, user_id, f.check_level FROM file f JOIN user u'
        ' ON f.user_id = u.id WHERE f.id = '+str(file_id)+' ORDER BY created, uploaded DESC'
    ).fetchone()

    if file['check_level'] == 0: # didn't make thumbnail
        cluster.make_thumbnail(file['user_id'], file_id, file['path'])

        db.execute(
            'UPDATE file SET check_level = ?'
            ' WHERE id = ?',
            (1, file_id)
        )
        db.commit()
        
    thumbs = db.execute(
        'SELECT thumb_path, file.id as file_id FROM file INNER JOIN face ON file.id = face.file_id and file.id = '+str(file_id)
    ).fetchall()    
    
    return render_template('file/file_detail.html', file=file, thumbs=thumbs)

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
                (g.user['id'], path, os.path.basename(path))
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

@bp.route('/<int:file_id>/update', methods=('GET','POST'))
@login_required
def update(file_id):
    file = get_file(file_id)

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
                (path, file_id)
            )
            db.commit()
            return redirect(url_for('file.index'))

    return render_template('file/update.html', file=file)

@bp.route('/<int:file_id>/delete', methods=('POST', ))
@login_required
def delete(file_id):
    get_file(file_id)
    db = get_db()
    db.execute('DELETE FROM file WHERE id = ?', (file_id,))
    db.commit()
    return redirect(url_for('file.index'))


@bp.route('/<int:file_id>/reset_level')
@login_required
def reset_level(file_id):
    get_file(file_id)
    db = get_db()
    db.execute('DELETE FROM face WHERE file_id = ?', (file_id,))
    db.execute('UPDATE file SET check_level = 0 WHERE id = ?', (file_id,))
    db.commit()
    return redirect(url_for('file.file_detail', file_id=file_id))
