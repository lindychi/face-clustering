from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from flask_clustering.auth import login_required
from flask_clustering.db import get_db

bp = Blueprint('resource', __name__, url_prefix='/resource')

@bp.route("/<path:path>")
def images(path):
    return flask.response(open(path).read())
