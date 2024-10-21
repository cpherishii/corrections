from flask import Blueprint

exercise_management = Blueprint('exercise_management', __name__, template_folder='templates/exercise_management')

from . import routes