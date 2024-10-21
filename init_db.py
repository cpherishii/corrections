from app import app, db
from models import Error, Correction, Topic, ErrorTopic, Rule, Example, RuleTopic

with app.app_context():
    db.create_all()