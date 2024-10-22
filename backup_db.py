from models import *
import pandas as pd
from app import app

with app.app_context():
    all_errors = Error.query.all()

    list_of_dicts = []

    for error in all_errors:
        incorrect_sentence = error.incorrect_sentence
        correct_sentences = '\n'.join([correction.correct_sentence for correction in error.corrections])
        topics = '\n'.join([error_topic.topic.topic_name for error_topic in error.error_topics])
        entered = error.entered
        
        error_dict = {'incorrect_sentence': incorrect_sentence,
                      'correct_sentences': correct_sentences,
                      'topics': topics,
                      'entered': entered}
        list_of_dicts.append(error_dict)

    errors_df = pd.DataFrame(list_of_dicts)

    errors_df.to_csv('all_errors.csv', sep=';')