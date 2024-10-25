from flask import render_template, redirect, url_for, request, session, flash
from app import app, current_user
from extensions import db
from models import List, ListItem, ClozeList, ClozeSentence, Error, Teacher, Student
from forms import EditListForm, WorksheetForm, EditClozeSentenceForm, ManageListForm
from sqlalchemy import desc
import random
from cloze import get_missing_words


@app.route('/lists', methods=['GET', 'POST'])
def lists():
    if isinstance(current_user, Teacher):
        lists = List.query.filter_by(teacher_id=current_user.id).order_by(desc(List.id)).all()
    elif isinstance(current_user, Student):
        lists = List.query.filter_by(student_id=current_user.id).order_by(desc(List.id)).all()
    else:
        lists = List.query.order_by(desc(List.id)).all()
    edit_list_form = EditListForm(csrf_enabled=False)
    if isinstance(current_user, Teacher):
        cloze_lists = ClozeList.query.filter_by(teacher_id=current_user.id).order_by(desc(ClozeList.id)).all()
    elif isinstance(current_user, Student):
        cloze_lists = ClozeList.query.filter_by(student_id=current_user.id).order_by(desc(ClozeList.id)).all()
    else:
        cloze_lists = ClozeList.query.order_by(desc(ClozeList.id)).all()
    edit_cloze_list_form = EditListForm()
    return render_template('lists.html', lists=lists, edit_list_form=edit_list_form, cloze_lists=cloze_lists,
                           edit_cloze_list_form=edit_cloze_list_form)

@app.route('/add_list_items', methods=['GET', 'POST'])
def add_list_items():
    list_form = ManageListForm()
    existing_lists = List.query.all()
    list_form.existing_list.choices = [('', 'Add to an Existing List')] + [(list.id, list.list_name) for list in existing_lists]
    #Process list form:
    if request.method == 'POST':
        print("Form Data: " + str(request.form))
        if list_form.validate_on_submit():
            selected_error_ids = request.form.get('selected_errors').split(',')
            print('Selected Errors: ' + str(selected_error_ids))
            existing_list_id = list_form.existing_list.data
            new_list_name = list_form.new_list_name.data
            if existing_list_id:
                list = List.query.get(existing_list_id)
                print('Existing List: ' + str(list.list_name))
                for error_id in selected_error_ids:
                    new_list_item = ListItem(list_id=list.id,
                                             error_id=error_id,)
                    db.session.add(new_list_item)
                try:
                    db.session.commit()
                    flash(f'{len(selected_error_ids)} sentences added to \"{list.list_name}\"')
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing to the database: {e}")
            elif new_list_name:
                print('New List Name: ' + str(new_list_name))
                new_list = List(list_name=new_list_name)
                db.session.add(new_list)
                try:
                    db.session.flush()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error flushing new_list to the database: {e}")
                for error_id in selected_error_ids:
                    new_list_item = ListItem(list_id=new_list.id,
                                             error_id=error_id,)
                    db.session.add(new_list_item)
                try:
                    db.session.commit()
                    flash(f'{len(selected_error_ids)} sentences added to \"{new_list.list_name}\"')
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing to the database: {e}")
            return redirect(url_for('index'))
        else:
            print('Form validation failed.')
            for fieldname, errorMessages in list_form.errors.items():
                for err in errorMessages:
                    print(f'Error in {fieldname}: {err}')
    return redirect(url_for('index'))

@app.route('/error_list/<int:list_id>', methods=['GET', 'POST'])
def error_list(list_id):
    list = List.query.get(list_id)
    edit_list_form = EditListForm()
    worksheet_form = WorksheetForm(title=list.list_name)
    if request.method == 'POST' and worksheet_form.validate_on_submit:
        title = request.form.get('title')
        worksheet_type = request.form.get('worksheet_type')
        exercise_id = int(request.form.get('exercise'))
        print('Exercise ID: ' + str(exercise_id))
        number_of_questions = request.form.get('number_of_questions')
        list_items = list.list_items
        
        
        if exercise_id == 1:
            if request.form.get('randomize'):
                random.shuffle(list_items)
            error_dicts = []
            correct_answers = 0
            incorrect_answers = 0
            for item in list_items:
                if correct_answers > 0:
                    show_correct = False
                    correct_answers = 0
                elif incorrect_answers > 3:
                    show_correct = True
                    incorrect_answers = 0
                else:
                    show_correct = random.choice([True, False])
                if show_correct:
                    correct_answers += 1
                    error_dict = {
                        'error_id': item.error_id,
                        'sentence_to_display': random.choice([correction.correct_sentence for correction in item.error.corrections]),
                        'answer': 'CORRECT',
                        'correct_sentences': [correction.correct_sentence for correction in item.error.corrections]
                        }
                    error_dicts.append(error_dict)
                else:
                    incorrect_answers += 1
                    error_dict = {
                        'error_id': item.error_id,
                        'sentence_to_display': item.error.incorrect_sentence,
                        'answer': 'INCORRECT',
                        'correct_sentences': [correction.correct_sentence for correction in item.error.corrections]
                    }
                    error_dicts.append(error_dict)
            session['questions'] = error_dicts
            print('Questions added to session: ' + str(session['questions']))
            return redirect(url_for('error_worksheet', list_id=list.id, title=title, worksheet_type=worksheet_type, 
                                    number_of_questions=number_of_questions, exercise_id=exercise_id))
        elif exercise_id == 2:
            if request.form.get('randomize'):
                random.shuffle(list_items)
            error_dicts = []
            for item in list_items:
                correct_first = random.choice([True, False])
                if correct_first:
                    error_dict = {
                        'sentence_a': random.choice([correction.correct_sentence for correction in item.error.corrections]),
                        'sentence_b': item.error.incorrect_sentence,
                        'answer': 'A'
                    }
                    error_dicts.append(error_dict)
                else:
                    error_dict = {
                        'sentence_a': item.error.incorrect_sentence,
                        'sentence_b': random.choice([correction.correct_sentence for correction in item.error.corrections]),
                        'answer': 'B'
                    }
                    error_dicts.append(error_dict)
            session['questions'] = error_dicts
            return redirect(url_for('error_worksheet', list_id=list.id, title=title, worksheet_type=worksheet_type, 
                        number_of_questions=number_of_questions, exercise_id=exercise_id))
        else:
            if request.form.get('randomize'):
                random.shuffle(list_items)
            error_dicts = []
            for item in list_items:
                error_dict = {
                    'incorrect_sentence': item.error.incorrect_sentence,
                    'correct_sentences': [correction.correct_sentence for correction in item.error.corrections]
                }
                error_dicts.append(error_dict)
            session['questions'] = error_dicts
            return redirect(url_for('error_worksheet', list_id=list.id, title=title, worksheet_type=worksheet_type, 
                                    number_of_questions=number_of_questions, exercise_id=exercise_id))
                
    return render_template('error_list.html', list=list, edit_list_form=edit_list_form, worksheet_form=worksheet_form)

@app.route('/cloze_list/<int:cloze_list_id>', methods=['GET', 'POST'])
def cloze_list(cloze_list_id):
    list = ClozeList.query.get(cloze_list_id)
    edit_list_form = EditListForm()
    worksheet_form = WorksheetForm(title=list.list_name)
    if request.method == 'POST' and worksheet_form.validate_on_submit:
        title = request.form.get('title')
        worksheet_type = request.form.get('worksheet_type')
        number_of_questions = request.form.get('number_of_questions')
        sentences = [sentence for sentence in list.cloze_sentences]
        if request.form.get('randomize'):
            random.shuffle(sentences)
        session['questions'] = sentences
        
        return redirect(url_for('cloze_worksheet', cloze_list_id=cloze_list_id,
                                title=title, worksheet_type=worksheet_type,
                                number_of_questions=number_of_questions))
    return render_template('cloze_list.html', list=list, edit_list_form=edit_list_form, worksheet_form=worksheet_form)


@app.route('/error_worksheet/<int:list_id>/<title>/<int:worksheet_type>/<int:number_of_questions>/<int:exercise_id>', methods=['GET', 'POST'])
def error_worksheet(list_id, title, worksheet_type, number_of_questions, exercise_id):
    list = List.query.get(list_id)
    questions = session['questions']
    if len(questions) >= number_of_questions:
        questions = questions[:number_of_questions]
    
    print('Questions: ' + str(questions))
    
    return render_template(f'error_worksheet_{exercise_id}.html', list=list, title=title, worksheet_type=worksheet_type, 
                           questions=questions, number_of_questions=number_of_questions)
    

@app.route('/cloze_worksheet/<int:cloze_list_id>/<title>/<int:worksheet_type>/<int:number_of_questions>', methods=['GET', 'POST'])
def cloze_worksheet(cloze_list_id, title, worksheet_type, number_of_questions):
    list = ClozeList.query.get(cloze_list_id)
    questions = session['questions']
    target_words = []
    for word in list.target_words.split('\n'):
        if word.strip('.') not in target_words:
            target_words.append(word.strip('.'))
    title = title
    worksheet_type = worksheet_type
    number_of_questions = number_of_questions
    if len(questions) >= number_of_questions:
        questions = questions[:number_of_questions]
    
    print('Questions: ' + str(questions))
    
    return render_template('cloze_worksheet.html', list=list, title=title, worksheet_type=worksheet_type, 
                           target_words=target_words, questions=questions, number_of_questions=number_of_questions)

@app.route('/manage_question/<exercise>/<int:list_id>/<title>/<int:worksheet_type>/<int:number_of_questions>/<int:index>/<action>')
def manage_question(exercise, list_id, title, worksheet_type, number_of_questions, index, action):
    questions = session['questions']
    if action == 'up':
        question = questions.pop(index)
        questions.insert(index-1, question)
        session['questions'] = questions
        session.modified = True
    elif action == 'down':
        question = questions.pop(index)
        questions.insert(index+1, question)
        session['questions'] = questions
        session.modified = True
    elif action == 'correct':
        question = questions[index]
        error = Error.query.filter_by(id=question['error_id']).first()
        if question['answer'] == 'CORRECT':
            question['sentence_to_display'] = error.incorrect_sentence
            question['answer'] = 'INCORRECT'
        else:
            question['sentence_to_display'] = random.choice([correction.correct_sentence for correction in error.corrections])
            question['answer'] = 'CORRECT'
        session.modified = True
    else:
        questions.pop(index)
        session['questions'] = questions
        session.modified = True
    if exercise == 'cloze':
        return redirect(url_for('cloze_worksheet', cloze_list_id=list_id, title=title, worksheet_type=worksheet_type, 
                                number_of_questions=number_of_questions))
    else: 
        exercise_id = int(exercise[-1])
        return redirect(url_for('error_worksheet', list_id=list_id, title=title, worksheet_type=worksheet_type,
                                number_of_questions=number_of_questions, exercise_id=exercise_id))


@app.route('/delete_list/<int:list_id>', methods=['GET', 'POST'])
def delete_list(list_id):
    list_to_delete = List.query.filter_by(id=list_id).first()
    db.session.delete(list_to_delete)
    try:
        db.session.commit()
        flash('List deleted successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('lists'))

@app.route('/delete_cloze_list/<int:cloze_list_id>', methods=['GET', 'POST'])
def delete_cloze_list(cloze_list_id):
    list_to_delete = ClozeList.query.filter_by(id=cloze_list_id).first()
    db.session.delete(list_to_delete)
    try:
        db.session.commit()
        flash('List deleted successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('lists'))

@app.route('/delete_lists', methods=['GET', 'POST'])
def delete_lists():
    if request.method == 'POST' and request.form.get('selected_list_ids'):
        selected_list_ids = request.form.get('selected_list_ids').split(',')
        print('Selected Lists: ' + str(selected_list_ids))
        for list_id in selected_list_ids:
            list_to_delete = List.query.get(list_id)
            db.session.delete(list_to_delete)
        try:
            db.session.commit()
            flash(f'{len(selected_list_ids)} lists successfully deleted')
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
    return redirect(url_for('lists'))

@app.route('/delete_cloze_lists', methods=['GET', 'POST'])
def delete_cloze_lists():
    if request.method == 'POST' and request.form.get('selected_cloze_list_ids'):
        selected_cloze_list_ids = request.form.get('selected_cloze_list_ids').split(',')
        print('Selected Cloze Lists: ' + str(selected_cloze_list_ids))
        for list_id in selected_cloze_list_ids:
            list_to_delete = ClozeList.query.get(list_id)
            db.session.delete(list_to_delete)
        try:
            db.session.commit()
            flash(f'{len(selected_cloze_list_ids)} lists successfully deleted')
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
    return redirect(url_for('lists'))

@app.route('/remove_list_item/<int:list_id>/<int:list_item_id>', methods=['GET', 'POST'])
def remove_list_item(list_id, list_item_id):
    list_item_to_remove = ListItem.query.get(list_item_id)
    db.session.delete(list_item_to_remove)
    try:
        db.session.commit()
        flash('Item removed successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('error_list', list_id = list_id))

@app.route('/remove_list_items/<int:list_id>', methods=['GET', 'POST'])
def remove_list_items(list_id):
    if request.method == 'POST' and request.form.get('selected_item_ids'):
        selected_item_ids = request.form.get('selected_item_ids').split(',')
        print('Selected Items: ' + str(selected_item_ids))
        for item_id in selected_item_ids:
            item_to_delete = ListItem.query.get(item_id)
            db.session.delete(item_to_delete)
        try:
            db.session.commit()
            flash(f'{len(selected_item_ids)} items successfully deleted')
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
    return redirect(url_for('error_list', list_id = list_id))

@app.route('/delete_cloze_sentence/<int:cloze_list_id>/<int:cloze_sentence_id>', methods=['GET', 'POST'])
def delete_cloze_sentence(cloze_list_id, cloze_sentence_id):
    cloze_sentence_to_delete = ClozeSentence.query.get(cloze_sentence_id)
    db.session.delete(cloze_sentence_to_delete)
    try:
        db.session.commit()
        flash('Sentence deleted successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('cloze_list', cloze_list_id = cloze_list_id))    

@app.route('/delete_cloze_sentences/<int:cloze_list_id>', methods=['GET', 'POST'])
def delete_cloze_sentences(cloze_list_id):
    if request.method == 'POST' and request.form.get('selected_item_ids'):
        selected_item_ids = request.form.get('selected_item_ids').split(',')
        print('Selected Items: ' + str(selected_item_ids))
        for item_id in selected_item_ids:
            item_to_delete = ClozeSentence.query.get(item_id)
            db.session.delete(item_to_delete)
        try:
            db.session.commit()
            flash(f'{len(selected_item_ids)} items successfully deleted')
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
    return redirect(url_for('cloze_list', cloze_list_id = cloze_list_id))

@app.route('/edit_list/<int:list_id>', methods=['GET', 'POST'])
def edit_list(list_id):
    list = List.query.filter_by(id=list_id).first()
    edit_list_form = EditListForm(list_name=list.list_name)
    if request.method == 'POST' and edit_list_form.validate_on_submit():
        list.list_name = request.form.get('list_name')
        try:
            db.session.commit()
            flash('List edited successfully.', category='success')
        except:
            db.session.rollback()
    return redirect(url_for('list', list_id=list_id))

@app.route('/edit_cloze_list/<int:cloze_list_id>', methods=['GET', 'POST'])
def edit_cloze_list(cloze_list_id):
    list = ClozeList.query.filter_by(id=cloze_list_id).first()
    edit_cloze_list_form = EditListForm(list_name=list.list_name)
    if request.method == 'POST' and edit_cloze_list_form.validate_on_submit():
        list.list_name = request.form.get('list_name')
        try:
            db.session.commit()
            flash('List edited successfully', category='success')
        except:
            db.session.rollback()
        return redirect(url_for('lists'))
    
    
@app.route('/edit_cloze_sentence/<int:cloze_list_id>/<int:cloze_sentence_id>', methods=['GET', 'POST'])
def edit_cloze_sentence(cloze_list_id, cloze_sentence_id):
    cloze_sentence = ClozeSentence.query.get(cloze_sentence_id)
    cloze_list = ClozeList.query.get(cloze_list_id)
    target_words = cloze_list.target_words.split('\n')
    edit_cloze_sentence_form = EditClozeSentenceForm(clozed_sentence=cloze_sentence.clozed_sentence,
                                                     original_sentences=cloze_sentence.original_sentences)
    if request.method == 'POST' and edit_cloze_sentence_form.validate_on_submit():
        if request.form.get('clozed_sentence'):
            clozed_sentence = request.form.get('clozed_sentence')
        else:
            clozed_sentence = cloze_sentence.clozed_sentence        
        new_original_sentences = [sentence.strip().strip('\n') for sentence in request.form.get('original_sentences').split('\n')]
        print(str(new_original_sentences))
        print('Clozed Sentence: ' + str(clozed_sentence))
        new_missing_words = get_missing_words(clozed_sentence, new_original_sentences)
        stripped_target_words = [word.strip('.') for word in target_words]
        for word_list in new_missing_words:
            for word in word_list:
                if word not in stripped_target_words:
                    return f'''\
                        Please make sure your cloze sentence and original sentences match up,
                        and that each new missing word is one of the original target words.\n
                        Your cloze sentence: {clozed_sentence}\n
                        Your original sentences: {new_original_sentences}\n
                        New missing words: {new_missing_words}'''
        
            
        joined_missing_words = ['/'.join(word_list) for word_list in new_missing_words]
        cloze_sentence.clozed_sentence = clozed_sentence
        cloze_sentence.original_sentences = '\n'.join(new_original_sentences)
        cloze_sentence.missing_words = '\n'.join(joined_missing_words)
        try:
            db.session.commit()
            flash('Sentence edited successfully.', category='success')
        except:
            db.session.rollback()                  
    return render_template('edit_cloze_sentence.html', cloze_sentence=cloze_sentence, edit_cloze_sentence_form=edit_cloze_sentence_form, cloze_list=cloze_list)