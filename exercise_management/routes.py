from flask import render_template, redirect, url_for, request, session, flash
from app import app, current_user
from extensions import db
from models import List, ListItem, ClozeList, ClozeSentence, Error, Topic, Teacher, Student
from forms import ErrorExerciseForm, ClozeExerciseForm, VerbFormExerciseForm
from cloze import create_cloze_list
from parse import get_verb_form_list
import random


@app.route('/exercises', methods=['GET', 'POST'])
def exercises():
    all_topics = Topic.query.order_by(Topic.topic_name).all()
    all_lists = List.query.all()
    all_cloze_lists = ClozeList.query.all()
    error_exercise_form = ErrorExerciseForm(csrf_enabled=False)
    error_exercise_form.topics.choices = [(topic.id, topic.topic_name) for topic in all_topics]
    error_exercise_form.existing_list.choices = [('', 'Study an existing list')] + \
                                                 [(list.id, list.list_name) for list in all_lists] 
    cloze_exercise_form = ClozeExerciseForm(csrf_enabled=False)
    cloze_exercise_form.existing_list.choices = [('', 'Study an existing list')] + \
                                                [(list.id, list.list_name) for list in all_cloze_lists]
    verb_form_exercise_form = VerbFormExerciseForm(csrf_enabled=False)
    
    #Create Exercise Form:
    if request.method == 'POST' and error_exercise_form.validate_on_submit():
        exercise_id = int(error_exercise_form.exercise.data)
        errors = []
            
        if error_exercise_form.topics.data:
            topic_ids = error_exercise_form.topics.data
            topic_ids = [int(topic_id) for topic_id in topic_ids]
            if request.form.get('list_name'):
                list_name = request.form.get('list_name')
            else:
                list_name = 'List ' + str(len(all_lists)+1)
            
            if isinstance(current_user, Teacher):
                print('Teacher:', current_user.username)
                new_list = List(teacher_id=current_user.id, list_name=list_name)
            elif isinstance(current_user, Student):
                new_list = List(student_id=current_user.id, list_name=list_name)
                print('Student:', current_user.username)
            else:
                new_list = List(list_name=list_name)
                print('No current user')
            db.session.add(new_list)
            try:
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(f"Error flushing new_rule to the database: {e}")
                return
            for topic_id in topic_ids:
                topic = Topic.query.filter_by(id=topic_id).first()
                topic_errors = topic.topic_errors
                for topic_error in topic_errors:
                    error = Error.query.filter_by(id=topic_error.error_id).first()
                    errors.append({
                                  'id': error.id,
                                  'incorrect_sentence': error.incorrect_sentence,
                                  'corrections': [correction.correct_sentence for correction in error.corrections],
                                  'topics': [{'id': error_topic.topic.id, 'topic_name': error_topic.topic.topic_name} for error_topic in error.error_topics],
                                  'rules': [{'id': error_rule.rule.id, 'rule_name': error_rule.rule.rule_name} for error_rule in error.error_rules],
                                  'correct_answers_needed': 3
                                  })
                    new_list_item = ListItem(error_id=error.id, list_id=new_list.id)
                    db.session.add(new_list_item)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error committing to the database: {e}")
            random.shuffle(errors)
            session['errors'] = errors
            return redirect(url_for('exercise', exercise_id=exercise_id, list_id=new_list.id, index=0))
            #return redirect(url_for('exercise', exercise_id=exercise_id, list_id=new_list.id, error_id=session['errors'][0]['id']))
        elif request.form.get('existing_list'):
            existing_list_id = request.form.get('existing_list')
            existing_list = List.query.get(existing_list_id)
            existing_list_items = ListItem.query.filter_by(list_id=existing_list_id).all()
            for item in existing_list_items:
                error = Error.query.get(item.error_id)
                errors.append({
                              'id': error.id,
                              'incorrect_sentence': error.incorrect_sentence,
                              'corrections': [correction.correct_sentence for correction in error.corrections],
                              'topics': [{'id': error_topic.topic.id, 'topic_name': error_topic.topic.topic_name} for error_topic in error.error_topics],
                              'rules': [{'id': error_rule.rule.id, 'rule_name': error_rule.rule.rule_name} for error_rule in error.error_rules],
                              'correct_answers_needed': 3
                              })
            random.shuffle(errors)
            print("Storing errors in session")
            session['errors'] = errors
            print("Errors stored in session, redirecting to exercise route")
            print("Errors: " + str(session['errors']))
            return redirect(url_for('exercise', exercise_id=exercise_id, list_id=existing_list_id, index=0))
            
    return render_template('exercises.html', error_exercise_form=error_exercise_form, cloze_exercise_form=cloze_exercise_form,
                           verb_form_exercise_form=verb_form_exercise_form)

@app.route('/create_cloze_exercise', methods=['GET', 'POST'])
def create_cloze_exercise():
    all_cloze_lists = ClozeList.query.all()
    cloze_exercise_form = ClozeExerciseForm(csrf_enabled=False)
    cloze_exercise_form.existing_list.choices = [('', 'Study an existing list')] + \
                                                [(list.id, list.list_name) for list in all_cloze_lists]
    #Cloze Exercise Form:
    if request.method == 'POST' and cloze_exercise_form.validate_on_submit():
        target_words = cloze_exercise_form.target_words.data.strip()
        existing_list_id = request.form['existing_list']
        if target_words:
            if request.form.get('list_name'):
                list_name = request.form.get('list_name')
            else:
                list_name = 'Gap-Fill List ' + str(len(all_cloze_lists)+1)
            target_words_list = cloze_exercise_form.target_words.data.split('\n')
            cloze_list = create_cloze_list(list_name, target_words_list)
            if len(cloze_list) > 0:
                random.shuffle(cloze_list)
                cloze_list_id = cloze_list[0]['cloze_list_id']
                session['cloze_list'] = cloze_list
                index = 0
            else:
                return 'There are no sentences in this list!'
        elif existing_list_id:
            list = ClozeList.query.get(existing_list_id)
            cloze_list = []
            target_words = [word for word in list.target_words.split('\n')]
            unique_target_words = []
            for word in target_words:
                if word.startswith('('):
                    word = word[word.find(')'):]
                elif word.endswith(')'):
                    word = word[:word.find('(')]
                if word.strip('.') not in unique_target_words:
                    unique_target_words.append(word.strip('.'))
            for sentence in list.cloze_sentences:
                list_item = {'id': sentence.id,
                              'cloze_list_id': list.id,
                              'target_words': unique_target_words,
                              'original_sentences': sentence.original_sentences.split('\n'),
                              'clozed_sentence': sentence.clozed_sentence,
                              'missing_words': [word.split('/') for word in sentence.missing_words.split('\n')],
                              'error_id': sentence.error_id,
                              'correct_answers_needed': 3}
                cloze_list.append(list_item)
            if len(cloze_list) > 0:
                cloze_list_id = existing_list_id
                random.shuffle(cloze_list)
                session['cloze_list'] = cloze_list
                index = 0
            else:
                return 'There are no sentences in this list!'
        else:
            print("No target words or existing list selected")
            # Handle the case where neither target words nor an existing list is provided
            flash("Please provide target words or select an existing list", "error")
            return redirect(url_for('exercises'))
        return redirect(url_for('cloze_exercise', cloze_list_id=cloze_list_id, index=index))

@app.route('/create_verb_form_exercise', methods=['GET', 'POST'])
def create_verb_form_exercise():
    verb_form_exercise_form = VerbFormExerciseForm()
    if request.method == 'POST' and verb_form_exercise_form.validate_on_submit:
        verb_forms = verb_form_exercise_form.verb_forms.data
        num_sentences = verb_form_exercise_form.num_sentences.data
        verb_form_list = get_verb_form_list(verb_forms, num_sentences)
        
        session['verb_form_list'] = verb_form_list
    return redirect(url_for('verb_form_exercise', verb_forms=verb_forms, index=0))

@app.route('/exercise/<int:exercise_id>/<int:list_id>/<int:index>', methods=['GET', 'POST'])
def exercise(exercise_id, list_id, index):
    if 'errors' not in session or not session['errors']:
        return redirect(url_for('exercises'))
    errors = session['errors']
    list_length = len(errors)
    list = List.query.get(list_id)
    if len(errors) == 0:
        return 'There are no sentences in this list!'
    error = errors[index]
    correct_sentences = [correction for correction in error['corrections']]
    #Next:
    if request.method == 'POST':
        action = request.form.get('action')
        result = request.form.get('result')
        print('Result: ' + str(result))
        if action == 'save':
            if result == 'correct':
                print("Answer: correct")
                errors[index]['correct_answers_needed'] -= 1
                session['errors'] = errors
                session.modified = True
                print("Correct answers needed: " + str(session['errors'][0]['correct_answers_needed']))                
                if errors[index]['correct_answers_needed'] == 0:
                    session['errors'] = [e for e in session['errors'] if e['incorrect_sentence'] != error['incorrect_sentence']]
                    session.modified = True
                    print("Sentence Deleted: " + str(error))
                    print("Session Errors: " + str(session['errors']))
            errors = session['errors']
            if len(errors) > index + 1:
                index += 1
            elif len(errors) > 0:
                index = 0
            else:
                flash('You have reached the end of this list!')
                return redirect(url_for('exercises'))
            return redirect(url_for('exercise', exercise_id=exercise_id, list_id=list_id, index=index))
        elif action == 'delete':
            if error:
                session['errors'] = [e for e in session['errors'] if e['incorrect_sentence'] != error['incorrect_sentence']]
                session.modified = True
                print("Sentence Deleted: " + str(error))
                print("Session Errors: " + str(session['errors']))
                error_to_delete = Error.query.filter_by(incorrect_sentence=error['incorrect_sentence']).first()
                if error_to_delete:
                    item_to_delete = ListItem.query.filter_by(error_id=error_to_delete.id).first()
                    if item_to_delete:
                        db.session.delete(item_to_delete)                
                        try:
                            db.session.commit()
                            flash('Item deleted successfully.')
                        except Exception as e:
                            db.session.rollback()
                            print(f"Error committing to the database: {e}")
                        if len(errors) == 0:
                            return 'There are no sentences in this list!'
                        return redirect(url_for('exercise', exercise_id=exercise_id, list_id=list_id, index=index))
    #Correct or Incorrect?
    if exercise_id == 1:
        show_correct = random.choice([True, False])
        if show_correct: 
            sentence_to_display = random.choice(error['corrections'])
        else:
            sentence_to_display = error['incorrect_sentence']
        return render_template('correct_or_incorrect.html', error=error, show_correct=show_correct, exercise_id=exercise_id,
                               sentence_to_display=sentence_to_display, correct_sentences=correct_sentences, list=list, 
                               index=index, list_length=list_length)
    #Choose the Correct Sentence:
    elif exercise_id == 2:
        correct_first = random.choice([True, False])
        if correct_first: 
            sentence1 = random.choice(error['corrections'])
            sentence2 = error['incorrect_sentence']
        else:
            sentence1 = error['incorrect_sentence']
            sentence2 = random.choice(error['corrections'])
        return render_template('choose_the_correct_sentence.html', error=error, correct_first=correct_first, exercise_id=exercise_id,
                               correct_sentences=correct_sentences, list=list, sentence1=sentence1, sentence2=sentence2, index=index, list_length=list_length)
    #Correct the Sentence:
    elif exercise_id == 3:
        incorrect_sentence = error['incorrect_sentence']
        correct_sentences = [correction for correction in error['corrections']]
        return render_template('correct_the_sentence.html', error=error, incorrect_sentence=incorrect_sentence,
                               correct_sentences=correct_sentences, exercise_id=exercise_id, list=list, 
                               index=index, list_length=list_length)
    else:
        random_exercise_id = random.choice(range(1, 4))
        if random_exercise_id == 1:
            show_correct = random.choice([True, False])
            if show_correct: 
                sentence_to_display = random.choice(error['corrections'])
            else:
                sentence_to_display = error['incorrect_sentence']
            return render_template('correct_or_incorrect.html', error=error, show_correct=show_correct, exercise_id=exercise_id,
                                   sentence_to_display=sentence_to_display, correct_sentences=correct_sentences, list=list, index=index, list_length=list_length)
        elif random_exercise_id == 2:
            correct_first = random.choice([True, False])
            if correct_first: 
                sentence1 = random.choice(error['corrections'])
                sentence2 = error['incorrect_sentence']
            else:
                sentence1 = error['incorrect_sentence']
                sentence2 = random.choice(error['corrections'])
            return render_template('choose_the_correct_sentence.html', error=error, correct_first=correct_first, exercise_id=exercise_id,
                                   correct_sentences=correct_sentences, list=list, sentence1=sentence1, sentence2=sentence2, index=index, list_length=list_length)
        elif random_exercise_id == 3:
            incorrect_sentence = error['incorrect_sentence']
            correct_sentences = [correction for correction in error['corrections']]
            return render_template('correct_the_sentence.html', error=error, incorrect_sentence=incorrect_sentence,
                                   correct_sentences=correct_sentences, exercise_id=exercise_id, list=list, index=index, list_length=list_length)



@app.route('/cloze_exercise/<int:cloze_list_id>/<int:index>', methods=['GET', 'POST'])
def cloze_exercise(cloze_list_id, index):
    if 'cloze_list' not in session or not session['cloze_list']:
        return redirect(url_for('exercises'))
    cloze_list = ClozeList.query.get(cloze_list_id)
    sentences = session['cloze_list']
    sentence = sentences[index]
    list_length = len(sentences)
    missing_words = sentence['missing_words']
    print('Missing words: ' + str(missing_words))
    error = Error.query.get(sentence['error_id'])
    #Next:
    if request.method == 'POST':
        action = request.form.get('action')
        result = request.form.get('result')
        print('Result: ' + str(result))
        if action == 'save':
            if result == 'correct':
                print("Answer: correct")
                sentences[index]['correct_answers_needed'] -= 1
                session['cloze_list'] = sentences
                session.modified = True
                print("Correct answers needed: " + str(session['cloze_list'][index]['correct_answers_needed']))                
                if sentences[index]['correct_answers_needed'] == 0:
                    session['cloze_list'] = [s for s in session['cloze_list'] if s['clozed_sentence'] != sentence['clozed_sentence']]
                    session.modified = True
                    print("Sentence Deleted: " + str(sentence))
                    print("Session Errors: " + str(session['cloze_list']))
                if len(sentences) == 0:
                    return 'There are no sentences in this list!'
            sentences = session['cloze_list']
            if len(sentences) > index + 1:
                index += 1
            elif len(sentences) > 0:
                index = 0
            else:
                flash('You have reached the end of this list!')
                return redirect(url_for('exercises'))
            return redirect(url_for('cloze_exercise', cloze_list_id=cloze_list_id, index=index))
        elif action == 'delete':
            if sentence:
                session['cloze_list'] = [e for e in session['cloze_list'] if e['clozed_sentence'] != sentence['clozed_sentence']]
                session.modified = True
                print("Sentence Deleted: " + str(sentence))
                print("Session Errors: " + str(session['cloze_list']))
                sentence_to_delete = ClozeSentence.query.filter_by(clozed_sentence=sentence['clozed_sentence']).first()
                if sentence_to_delete:
                    db.session.delete(sentence_to_delete)                
                    try:
                        db.session.commit()
                        flash('Item deleted successfully.')
                    except Exception as e:
                        db.session.rollback()
                        print(f"Error committing to the database: {e}")
                    if len(sentences) == 0:
                        return 'There are no sentences in this list!'
                    return redirect(url_for('cloze_exercise', cloze_list_id=cloze_list_id, index=index))
    return render_template('cloze_exercise.html', sentence=sentence, cloze_list_id=cloze_list.id, 
                                                  missing_words=missing_words, error=error, list_length=list_length, 
                                                  cloze_list=cloze_list, index=index)
    
@app.route('/verb_form_exercise/<verb_forms>/<int:index>', methods=['GET', 'POST'])
def verb_form_exercise(verb_forms, index):
    verb_form_list = session['verb_form_list']
    sentence_dict = verb_form_list[index]
    word_list = sentence_dict['word_list']
    error = Error.query.get(sentence_dict['error_id'])
    num_verb_forms = 0
    for word in word_list:
        if len(word) > 1:
            num_verb_forms += 1
    
    #Next:
    if request.method == 'POST':
        action = request.form.get('action')
        result = request.form.get('result')
        print('Result: ' + str(result))
        if action == 'save':
            if result == 'correct':
                print("Answer: correct")
                verb_form_list[index]['correct_answers_needed'] -= 1
                session['verb_form_list'] = verb_form_list
                session.modified = True
                print("Correct answers needed: " + str(session['verb_form_list'][index]['correct_answers_needed']))                
                if verb_form_list[index]['correct_answers_needed'] == 0:
                    session['verb_form_list'] = [sd for sd in session['verb_form_list'] if sd['word_list'] != sentence_dict['word_list']]
                    session.modified = True
                    print("Sentence Deleted: " + str(sentence_dict))
                    print("Session Sentences: " + str(session['verb_form_list']))
                if len(verb_form_list) == 0:
                    return 'There are no sentences in this list!'
            verb_form_list = session['verb_form_list']
            if len(verb_form_list) > index + 1:
                index += 1
            elif len(verb_form_list) > 0:
                index = 0
            else:
                flash('You have reached the end of this list!')
                return redirect(url_for('exercises'))
            return redirect(url_for('verb_form_exercise', verb_forms=verb_forms, index=index))
        elif action == 'delete':
            if sentence_dict:
                session['verb_form_list'] = [sd for sd in session['verb_form_list'] if sd['word_list'] != sentence_dict['verb_form_list']]
                session.modified = True
                print("Sentence Deleted: " + str(sentence_dict))
                print("Session Errors: " + str(session['verb_form_list']))
                if len(verb_form_list) == 0:
                    return 'There are no sentences in this list!'
                return redirect(url_for('verb_form_exercise', verb_forms=verb_forms, index=index))
    return render_template('verb_form_exercise.html', verb_forms=verb_forms, verb_form_list=verb_form_list,
                       sentence_dict=sentence_dict, index=index, error=error, num_verb_forms=num_verb_forms)