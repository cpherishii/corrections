from flask import Blueprint

list_management = Blueprint('list_management', __name__, template_folder='templates/list_management')

from . import routes