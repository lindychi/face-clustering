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
    return render_template('file/index.html', files=get_page_files(0), count=get_total_count_range())

@bp.route('/<int:page_index>')
@login_required
def index_page(page_index=0):
    return render_template('file/index.html', files=get_page_files(page_index), count=get_total_count_range())

def get_total_count_range():
    return range(get_total_count())

def get_total_count(): 
    db = get_db()
    count = db.execute(
        'SELECT count(*) FROM file f JOIN user u'
        ' ON f.user_id = u.id and u.id = '+str(g.user['id'])
    ).fetchone()
    return int(count[0] / 50) # page count

def get_page_files(page_index=0):
    db = get_db()
    files = db.execute(
        'SELECT f.id, f.name, f.path, f.created, f.uploaded, username, user_id, f.check_level FROM file f JOIN user u'
        ' ON f.user_id = u.id and u.id = '+str(g.user['id'])+' ORDER BY f.uploaded DESC LIMIT 50 OFFSET '+str(page_index*50)
    ).fetchall()
    return files

@bp.route('/detail/<int:file_id>')
def file_detail(file_id):
    db = get_db()
    file = db.execute(
        'SELECT f.id, f.name, f.path, f.created, f.uploaded, username, user_id, f.check_level FROM file f JOIN user u'
        ' ON f.user_id = u.id WHERE f.id = '+str(file_id)+' ORDER BY created, uploaded DESC'
    ).fetchone()
        
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
            add_file(path)
            return redirect(url_for('file.index'))
    return render_template('file/create.html')

def add_file(path, is_commit=True, db=None):
    if not db:
        db = get_db()

    db.execute(
        'INSERT INTO file (user_id, path, name)'
        ' VALUES (?, ?, ?)',
        (g.user['id'], path, os.path.basename(path))
    )

    if is_commit:
        db.commit()

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

def get_files_in_level(level):
    db = get_db()

    return db.execute(
        'SELECT f.id, f.path FROM file f JOIN user u ON f.user_id = u.id and u.id = '+str(g.user['id'])+' WHERE check_level = '+str(level)
    ).fetchall()

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

@bp.route('/cluster')
@login_required
def clustering():
    c = cluster.Cluster()
    c.get_encoding_from_files()
    # c.cluster()
    
