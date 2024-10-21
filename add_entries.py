from app import app, db
from errors import errors
from models import *

errors_reversed = list(reversed(errors))

with app.app_context():
    #db.drop_all()
    #db.create_all()
    for error in errors_reversed:
        existing_error = Error.query.filter_by(incorrect_sentence = error['incorrect sentence'].strip().replace("’", "'")).first()
        if existing_error:
            continue
        else:
            new_error = Error(incorrect_sentence = error['incorrect sentence'].strip().replace("’", "'"),
                              entered=datetime.now(timezone.utc))
            db.session.add(new_error)
            try:
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(f"Error flushing new_error to the database: {e}")
                continue
            for correction in error['correct sentence']:
                new_correction = Correction(correct_sentence = correction.strip().replace("’", "'"), 
                                            error_id = new_error.id)
                db.session.add(new_correction)
        #for topic in error['topic']:
        #    existing_topic = Topic.query.filter_by(topic_name = topic).first()
        #    if existing_topic:
        #        topic_id = existing_topic.id
        #    else:
        #        new_topic = Topic(topic_name = topic)
        #        db.session.add(new_topic)
        #        try:
        #            db.session.flush()
        #        except Exception as e:
        #            db.session.rollback()
        #            print(f"Error flushing new_topic to the database: {e}")
        #            continue
        #        topic_id = new_topic.id
        #    new_error_topic = ErrorTopic(error_id = new_error.id, topic_id = topic_id)
        #    db.session.add(new_error_topic)
            
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error committing to the database: {e}")
    
