import os
from urllib import parse
from flask import (
    Blueprint, send_from_directory, send_file
)

from . import cluster

from flask_clustering.auth import login_required
from flask_clustering.db import get_db

bp = Blueprint('resource', __name__, url_prefix='/resource')

@bp.route("/<path:path>")
def get_image_url(path):
    path=parse.unquote("/"+path)
    return send_from_directory(os.path.dirname(path),
                               os.path.basename(path))


@bp.route("/located/<path:path>")
def get_located_image_url(path):
    path=parse.unquote("/"+path)
    path=cluster.get_located_image_path(path)
    return send_from_directory(os.path.dirname(path),
                               os.path.basename(path))

