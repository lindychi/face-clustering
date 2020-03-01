import os
from urllib import parse
from flask import (
    Blueprint, send_from_directory
)

from flask_clustering.auth import login_required
from flask_clustering.db import get_db

bp = Blueprint('resource', __name__, url_prefix='/resource')

@bp.route("/<path:path>")
def images(path):
    path=parse.unquote("/"+path)
    return send_from_directory(os.path.dirname(path),
                               os.path.basename(path))
