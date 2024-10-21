from extensions import db
import os
import csv
from models import *
from flask import flash


CSV_FOLDER = os.path.join(os.path.dirname(__file__), 'csv')

def load_csv_files():
    errors = []
    for filename in os.listdir(CSV_FOLDER):
        #if filename.endswith('.csv'):
        if filename == 'to_add.csv':
            filepath = os.path.join(CSV_FOLDER, filename)
            with open(filepath, newline='') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=';')
                for row in csv_reader:
                    new_sentence = {}
                    new_sentence['incorrect sentence'] = row['incorrect sentence'].strip().replace("’", "'")
                    new_sentence['correct sentence'] = [sentence.strip().replace("’", "'") for sentence in row['correct sentence'].split('\n')]
                    new_sentence['topic'] = [topic.strip().replace("’", "'") for topic in row['topic'].split('\n')]
                    errors.append(new_sentence)
    unique_errors = []
    seen_sentences = []
    for error in errors:
        if error['incorrect sentence'] not in seen_sentences:
            seen_sentences.append(error['incorrect sentence'])
            unique_error = {
                'incorrect sentence': error['incorrect sentence'],
                'correct sentence': [],
                'topic': []
            }
            for correction in error['correct sentence']:
                if correction not in unique_error['correct sentence']:
                    unique_error['correct sentence'].append(correction)
            for error in errors:
                if unique_error['incorrect sentence'] == error['incorrect sentence']:
                    for topic in error['topic']:
                        if topic not in unique_error['topic']:
                            unique_error['topic'].append(topic)
            unique_errors.append(unique_error)
    return unique_errors
    
errors = load_csv_files()

def add_error(teacher_id=None, incorrect_sentence=None, correct_sentences=None, topics=None, rules=None, 
              new_topic_name=None, new_rule_name=None, new_rule_text=None, new_rule_topic_ids=None):
    
    new_error = Error(teacher_id=teacher_id,
                      incorrect_sentence=incorrect_sentence.strip().replace("’", "'"),
                      entered=datetime.now(timezone.utc))
    db.session.add(new_error)
    try:
        db.session.flush()
    except Exception as e:
        db.session.rollback()
        print(f"Error flushing new_error to the database: {e}")
        return
    #Add list of correct sentences:
    if correct_sentences:
        for correct_sentence in correct_sentences:
            new_correction = Correction(correct_sentence=correct_sentence.strip().replace("’", "'"), error_id = new_error.id)
            db.session.add(new_correction)
    #Add list of topics:
    if topics:
        for topic in topics:
            topic_to_add = Topic.query.filter_by(topic_name=topic).first()
            if topic_to_add:
                new_error_topic = ErrorTopic(error_id=new_error.id, topic_id=topic_to_add.id)
                db.session.add(new_error_topic)
    #Add list of rules:
    if rules:
        for rule in rules:
            rule_to_add = Rule.query.filter_by(rule_name=rule).first()
            if rule_to_add:
                new_error_rule = ErrorRule(error_id=new_error.id, rule_id=rule_to_add.id)
                db.session.add(new_error_rule)
    #Define new topic:
    if new_topic_name:
        #new_topic_name = new_topic_name if new_topic_name is not None else ""
        new_topic = Topic(topic_name=new_topic_name.strip().replace("’", "'"))
        db.session.add(new_topic)
        try:
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            print(f"Error flushing new_rule to the database: {e}")
            return
        new_error_topic = ErrorTopic(error_id=new_error.id, topic_id=new_topic.id)
        db.session.add(new_error_topic)
    #Define new rule:
    if new_rule_name:
        #new_rule_text = new_rule_text if new_rule_text is not None else ""
        new_rule = Rule(rule_name=new_rule_name.strip().replace("’", "'"), rule_text=new_rule_text.strip().replace("’", "'"))
        db.session.add(new_rule)
        try:
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            print(f"Error flushing new_rule to the database: {e}")
            return
        #Add rule topics:
        if new_rule_topic_ids:
            for new_rule_topic_id in new_rule_topic_ids:
                new_rule_topic = RuleTopic(rule_id=new_rule.id, topic_id=new_rule_topic_id)
                db.session.add(new_rule_topic)
        new_error_rule = ErrorRule(error_id=new_error.id, rule_id=new_rule.id)
        db.session.add(new_error_rule)
    try:
        db.session.commit()
        flash('Sentence added successfully.', category='success')
    except Exception as e:
        db.session.rollback()
        print(f"Error committing to the database: {e}")



def edit_error(error_id, incorrect_sentence, correct_sentences, topics=None, rules=None, 
               new_topic_name=None, new_rule_name=None, new_rule_text=None, new_rule_topic_ids=None):
    #Edit incorrect sentence:
    error = Error.query.get(error_id)
    if not error:
        print(f"Error: no error found with id {error_id}")
        return
    if incorrect_sentence.strip().replace("’", "'") != error.incorrect_sentence:
        error.incorrect_sentence = incorrect_sentence.strip().replace("’", "'")
    #Delete existing corrections:
    existing_corrections = Correction.query.filter_by(error_id=error.id).all()
    for correction in existing_corrections:
        db.session.delete(correction)
    #Add new corrections:
    if correct_sentences:
        for correct_sentence in correct_sentences:
            new_correction = Correction(correct_sentence=correct_sentence.strip().replace("’", "'"), 
                                            error_id = error.id)
            db.session.add(new_correction)
    #Check for existing error topics and add new ones:
    if topics:
        existing_error_topics = ErrorTopic.query.filter_by(error_id=error.id).all()
        existing_topics = [Topic.query.filter_by(id=error_topic.topic_id).first() for error_topic in existing_error_topics]
        existing_topic_names = [topic.topic_name for topic in existing_topics]
        for topic in topics:
            if topic not in existing_topic_names:
                topic_id = Topic.query.filter_by(topic_name=topic).first().id
                new_error_topic = ErrorTopic(error_id=error.id, topic_id=topic_id)
                db.session.add(new_error_topic)
    #Check for existing error rules and add new ones:
    if rules:
        existing_error_rules = ErrorRule.query.filter_by(error_id=error.id).all()
        existing_rules = [Rule.query.filter_by(id=error_rule.rule_id).first() for error_rule in existing_error_rules]
        existing_rule_names = [rule.rule_name for rule in existing_rules]
        for rule in rules:
            if rule not in existing_rule_names:
                rule_id = Rule.query.filter_by(rule_name=rule).first().id
                new_error_rule = ErrorRule(error_id=error.id, rule_id=rule_id)
                db.session.add(new_error_rule)
    #Define new topic:
    if new_topic_name:
        new_topic_name = new_topic_name.strip().replace("’", "'")
        existing_topic = Topic.query.filter_by(topic_name=new_topic_name).first()
        if existing_topic:
            return 'This topic already exists.'
        else:
            new_topic_name = new_topic_name if new_topic_name is not None else ""
            new_topic = Topic(topic_name=new_topic_name)
            db.session.add(new_topic)
            try:
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(f"Error flushing new_rule to the database: {e}")
                return
            new_error_topic = ErrorTopic(error_id=error.id, topic_id=new_topic.id)
            db.session.add(new_error_topic)
    #Define new rule:
    if new_rule_name:
        new_rule_name = new_rule_name.strip().replace("’", "'")
        existing_rule = Rule.query.filter_by(rule_name=new_rule_name).first()
        if existing_rule:
            return 'This rule already exists.'
        else:
            new_rule_text = new_rule_text.strip().replace("’", "'") if new_rule_text is not None else ""
            new_rule = Rule(rule_name=new_rule_name, rule_text=new_rule_text)
            db.session.add(new_rule)
            try:
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(f"Error flushing new_rule to the database: {e}")
                return
            #Add rule topics:
            if new_rule_topic_ids:
                for new_rule_topic_id in new_rule_topic_ids:
                    new_rule_topic = RuleTopic(rule_id=new_rule.id, topic_id=new_rule_topic_id)
                    db.session.add(new_rule_topic)
            new_error_rule = ErrorRule(error_id=error.id, rule_id=new_rule.id)
            db.session.add(new_error_rule)
    error.last_edited = datetime.now(timezone.utc)
    try:
        db.session.commit()
        flash('Sentence edited successfully.', category='success')
    except Exception as e:
        db.session.rollback()
        print(f"Error committing to the database: {e}")    


def add_rules_and_topics_handler(error_id, topics=None, rules=None, new_topic_name=None, 
                         new_rule_name=None, new_rule_text=None, new_rule_topic_ids=None):
    error = Error.query.get(error_id)
    if not error:
        print(f"Error: no error found with id {error_id}")
        return
    #Check for existing error topics and add new ones:
    if topics:
        existing_error_topics = ErrorTopic.query.filter_by(error_id=error.id).all()
        existing_topics = [Topic.query.filter_by(id=error_topic.topic_id).first() for error_topic in existing_error_topics]
        existing_topic_names = [topic.topic_name for topic in existing_topics]
        for topic in topics:
            if topic not in existing_topic_names:
                topic_id = Topic.query.filter_by(topic_name=topic).first().id
                new_error_topic = ErrorTopic(error_id=error.id, topic_id=topic_id)
                db.session.add(new_error_topic)
    #Check for existing error rules and add new ones:
    if rules:
        existing_error_rules = ErrorRule.query.filter_by(error_id=error.id).all()
        existing_rules = [Rule.query.filter_by(id=error_rule.rule_id).first() for error_rule in existing_error_rules]
        existing_rule_names = [rule.rule_name for rule in existing_rules]
        for rule in rules:
            if rule not in existing_rule_names:
                rule_id = Rule.query.filter_by(rule_name=rule).first().id
                new_error_rule = ErrorRule(error_id=error.id, rule_id=rule_id)
                db.session.add(new_error_rule)
    #Define new topic:
    if new_topic_name:
        existing_topic = Topic.query.filter_by(topic_name=new_topic_name).first()
        if existing_topic:
            return 'This topic already exists.'
        else:
            new_topic_name = new_topic_name if new_topic_name is not None else ""
            new_topic = Topic(topic_name=new_topic_name)
            db.session.add(new_topic)
            try:
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(f"Error flushing new_rule to the database: {e}")
                return
            new_error_topic = ErrorTopic(error_id=error.id, topic_id=new_topic.id)
            db.session.add(new_error_topic)
    #Define new rule:
    if new_rule_name:
        existing_rule = Rule.query.filter_by(rule_name=new_rule_name).first()
        if existing_rule:
            return 'This rule already exists.'
        else:
            new_rule_text = new_rule_text if new_rule_text is not None else ""
            new_rule = Rule(rule_name=new_rule_name, rule_text=new_rule_text)
            db.session.add(new_rule)
            try:
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(f"Error flushing new_rule to the database: {e}")
                return
            #Add rule topics:
            if new_rule_topic_ids:
                for new_rule_topic_id in new_rule_topic_ids:
                    new_rule_topic = RuleTopic(rule_id=new_rule.id, topic_id=new_rule_topic_id)
                    db.session.add(new_rule_topic)
            new_error_rule = ErrorRule(error_id=error.id, rule_id=new_rule.id)
            db.session.add(new_error_rule)
    error.last_edited = datetime.now(timezone.utc)
    try:
        db.session.commit()
        flash('Sentence updated successfully.', category='success')
    except Exception as e:
        db.session.rollback()
        print(f"Error committing to the database: {e}")        

        

        
        
        
        
        
        
        
        
        
        
        