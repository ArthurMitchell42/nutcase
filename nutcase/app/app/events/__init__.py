from flask import Blueprint

bp = Blueprint('events', __name__)

from app.events import routes
