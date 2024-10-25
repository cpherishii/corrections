from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from extensions import db
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import os
import shutil
import atexit
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'golunculus'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///errors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'

csrf = CSRFProtect(app)

SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
app.config['SESSION_FILE_DIR'] = SESSION_FILE_DIR
if not os.path.exists(SESSION_FILE_DIR):
    os.makedirs(SESSION_FILE_DIR)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session'
    
print(f"Session files will be stored in: {SESSION_FILE_DIR}")
    
db.init_app(app)
Session(app)



login_manager = LoginManager()
login_manager.init_app(app)

def teacher_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not isinstance(current_user, Teacher):
            return login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view

@login_manager.user_loader
def load_user(user_id):
    user_type, user_id = user_id.split(':') 
    if user_type == 'teacher':
        return Teacher.query.get(int(user_id))
    elif user_type == 'student':
        return Student.query.get(int(user_id))
    return None


@login_manager.unauthorized_handler
def unauthorized():
    return 'You are not logged in.'

from models import *
from errors import add_error, edit_error, add_rules_and_topics_handler
from forms import *
from parse import parse_text, explain_pos_tag, get_word_forms

from auth import auth as auth_blueprint
from list_management import list_management as list_management_blueprint
from exercise_management import exercise_management as exercise_management_blueprint
from user import user as user_blueprint

with app.app_context():

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(list_management_blueprint, url_prefix='/list_management')
    app.register_blueprint(exercise_management_blueprint, url_prefix='/exercise_management')
    app.register_blueprint(user_blueprint, url_prefix='/user')



@app.route('/list_sessions')
def list_sessions():
    if not os.path.exists(SESSION_FILE_DIR):
        return "Session directory does not exist."
    
    session_files = os.listdir(SESSION_FILE_DIR)
    if not session_files:
        return "No session files found."
    
    return f"Session files: {session_files}"

# Cleanup function to delete session files
def cleanup_session_files():
    if os.path.exists(SESSION_FILE_DIR):
        shutil.rmtree(SESSION_FILE_DIR)
        print("Session files deleted.")

# Register the cleanup function to be called on app exit
atexit.register(cleanup_session_files)






@app.route('/', methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        if isinstance(current_user, Teacher):
            return redirect(url_for('teacher_dashboard', user_id=current_user.id))
        elif isinstance(current_user, Student):
            return redirect(url_for('student_dashboard', user_id=current_user.id))
    
    all_topics = Topic.query.order_by(Topic.topic_name).all()
    all_rules = Rule.query.order_by(Rule.rule_name).all()
    topic_select_options = [('', 'Recent')] + [(topic.id, topic.topic_name) for topic in all_topics]
    select_topic_form = SelectTopicForm()
    select_topic_form.selected_topic.choices = topic_select_options
    
    list_form = ManageListForm()
    existing_lists = List.query.all()
    list_form.existing_list.choices = [('', 'Add to an Existing List')] + [(list.id, list.list_name) for list in list(reversed(existing_lists))]
    
    topic_tags = [('', 'Select a Topic (optional)')] + [(topic.id, topic.topic_name) for topic in all_topics]
    rule_tags = [('', 'Select a Rule (optional)')] + [(rule.id, rule.rule_name) for rule in all_rules]
    add_form = AddForm()
    add_form.topic1.choices = topic_tags
    add_form.topic2.choices = topic_tags
    add_form.topic3.choices = topic_tags
    add_form.rule1.choices = rule_tags
    add_form.rule2.choices = rule_tags
    add_form.rule3.choices = rule_tags
    add_form.rule_topic1.choices = topic_tags
    add_form.rule_topic2.choices = topic_tags
    add_form.rule_topic3.choices = topic_tags
               
    #Process add form:
    if request.method == 'POST' and add_form.validate_on_submit():
        if isinstance(current_user, Teacher):
            teacher_id = current_user.id
        else:
            teacher_id = None
        incorrect_sentence = request.form['error']
        correct_sentences = request.form['correction'].split('\n')        
        topics = []
        rules = []
        new_topic_name = None
        new_rule_name = None
        new_rule_text = None
        new_rule_topic_ids = []
        
        existing_error = Error.query.filter_by(incorrect_sentence=incorrect_sentence).first()
        if existing_error:
            flash('This sentence already exists.', category='error')
        #Add topics:
        for i in range(1, 4):
            topic_id = request.form.get(f'topic{i}')
            if topic_id:
                topic = Topic.query.get(topic_id)
                if topic:
                    topics.append(topic.topic_name)
        #Add Rules:
        for i in range(1, 4):
            rule_id = request.form.get(f'rule{i}')
            if rule_id:
                rule = Rule.query.get(rule_id)
                if rule:
                    rules.append(rule.rule_name)
        #Define new topic:
        if request.form.get('new_topic_name'):
            existing_topic = Topic.query.filter_by(topic_name=new_topic_name).first()
            if existing_topic:
                print('This topic already exists.')
                return 'This topic already exists.'
            else:
                new_topic_name = request.form['new_topic_name'].strip()
                if not new_topic_name:
                    new_topic_name = None
        #Define new rule:
        if request.form.get('new_rule_name'):
            existing_rule = Rule.query.filter_by(rule_name=request.form['new_rule_name']).first()
            if existing_rule:
                flash('This rule already exists.', category='error')
                return 'This rule already exists.'
            else:
                new_rule_name = request.form['new_rule_name'].strip()
                new_rule_text = request.form['new_rule_text'].strip()
                if not new_rule_name:
                    new_rule_name = None
                if not new_rule_text:
                    new_rule_text = None
                #if request.form.get('new_rule_text'):
                #    new_rule_text = request.form['new_rule_text']
                for i in range(1, 4):
                    rule_topic_id = request.form.get(f'rule_topic{i}')
                    if rule_topic_id:
                        new_rule_topic_ids.append(rule_topic_id)
    
        # Log the values being passed to add_error for debugging
        print("Incorrect Sentence:", incorrect_sentence)
        print("Correct Sentences:", correct_sentences)
        print("Topics:", topics)
        print("Rules:", rules)
        print("New Topic Name:", new_topic_name)
        print("New Rule Name:", new_rule_name)
        print("New Rule Text:", new_rule_text)
        print("New Rule Topic IDs:", new_rule_topic_ids)
    
        add_error(teacher_id, incorrect_sentence, correct_sentences, topics, rules,
                  new_topic_name, new_rule_name, new_rule_text, new_rule_topic_ids)
        return redirect(url_for('index'))
    
    topic = None
    errors = db.session.query(Error).outerjoin(ErrorTopic).options(joinedload(Error.corrections))\
            .order_by(desc(Error.entered)).limit(100).all()
            
    #Select topic form:
    if request.method == 'POST' and select_topic_form.validate_on_submit():
        topic_id = select_topic_form.selected_topic.data
        topic = Topic.query.get(topic_id)
        if topic:
            errors = db.session.query(Error).outerjoin(ErrorTopic).options(joinedload(Error.corrections))\
                    .filter(ErrorTopic.topic_id==topic.id).order_by(desc(Error.id)).all()
    
    return render_template('index.html', errors=errors, add_form=add_form, 
                           #add_form=add_form 
                           select_topic_form=select_topic_form, list_form=list_form)


@app.route('/edit/<int:error_id>', methods=['GET', 'POST'])
def edit(error_id):
    error = Error.query.get_or_404(error_id)
    corrections = '\n'.join([correction.correct_sentence for correction in error.corrections])
    topics = [error_topic.topic.id for error_topic in error.error_topics]
    rules = [error_rule.rule.id for error_rule in error.error_rules]
    #Populate topics and rules dynamically:
    all_topics = Topic.query.order_by(Topic.topic_name).all()
    all_rules = Rule.query.order_by(Rule.rule_name).all()
    topic_tags = [('', 'Select a Topic (optional)')] + [(topic.id, topic.topic_name) for topic in all_topics]
    rule_tags = [('', 'Select a Rule (optional)')] + [(rule.id, rule.rule_name) for rule in all_rules]
    
    edit_form = EditForm(error=error.incorrect_sentence,
                         correction=corrections)
    #Set choices for the form fields:
    edit_form.topic1.choices = topic_tags
    edit_form.topic2.choices = topic_tags
    edit_form.topic3.choices = topic_tags
    edit_form.rule1.choices = rule_tags
    edit_form.rule2.choices = rule_tags
    edit_form.rule3.choices = rule_tags
    edit_form.rule_topic1.choices = topic_tags
    edit_form.rule_topic2.choices = topic_tags
    edit_form.rule_topic3.choices = topic_tags    

    topics = []
    rules = []
    new_topic_name = None
    new_rule_name = None
    new_rule_text = None
    new_rule_topic_ids = []
    
    #Process edit form:
    if request.method == 'POST' and edit_form.validate_on_submit():
        incorrect_sentence = request.form['error']
        correct_sentences = request.form['correction'].split('\n')
        #Add topics:
        for i in range(1, 4):
            topic_id = request.form.get(f'topic{i}')
            if topic_id:
                topic = Topic.query.get(topic_id)
                if topic:
                    topics.append(topic.topic_name)
        #Add Rules:
        for i in range(1, 4):
            rule_id = request.form.get(f'rule{i}')
            if rule_id:
                rule = Rule.query.get(rule_id)
                if rule:
                    rules.append(rule.rule_name)
        #Define new topic:
        if request.form.get('new_topic_name'):
            existing_topic = Topic.query.filter_by(topic_name=request.form['new_topic_name']).first()
            if existing_topic:
                return 'This topic already exists.'
            else:
                new_topic_name = request.form['new_topic_name'].strip()
                if not new_topic_name:
                    new_topic_name = None
        #Define new rule:
        if request.form.get('new_rule_name'):
            existing_rule = Rule.query.filter_by(rule_name=request.form['new_rule_name']).first()
            if existing_rule:
                return 'This rule already exists.'
            else:
                new_rule_name = request.form['new_rule_name'].strip()
                new_rule_text = request.form['new_rule_text'].strip()
                if not new_rule_name:
                    new_rule_name = None
                if not new_rule_text:
                    new_rule_text = None
                for i in range(1, 4):
                    rule_topic_id = request.form.get(f'rule_topic{i}')
                    if rule_topic_id:
                        new_rule_topic_ids.append(rule_topic_id)
        edit_error(error_id, incorrect_sentence, correct_sentences, topics, rules,
                   new_topic_name, new_rule_name, new_rule_text, new_rule_topic_ids)
        return redirect(url_for('edit', error_id=error_id))
    return render_template('edit.html', edit_form=edit_form, error=error)


@app.route('/error_comment/<int:error_id>', methods=['GET', 'POST'])
def error_comment(error_id):
    error = Error.query.filter_by(id=error_id).first()
    error_comment_form = AddCommentForm()
    
    if request.method == 'POST' and error_comment_form.validate_on_submit():
        if error_comment_form.subject_heading.data:
            subject_heading = error_comment_form.subject_heading.data
        else:
            subject_heading = '(None)'
        new_comment = Comment(subject_heading = subject_heading,
                              message = error_comment_form.message.data,
                              error_id = error_id)
        db.session.add(new_comment)
        try:
            db.session.commit()
            flash('Comment added successfully.', category='success')
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
    return render_template('error_comment.html', error=error, error_comment_form=error_comment_form)

@app.route('/delete_comment/<int:comment_id>', methods=['GET', 'POST'])
def delete_comment(comment_id):
    comment_to_delete = Comment.query.filter_by(id=comment_id).first()
    error_id = comment_to_delete.error_id
    
    db.session.delete(comment_to_delete)
    try:
        db.session.commit()
        flash('Comment deleted successfully.', category='success')
    except Exception as e:
        db.session.rollback()
        print('Error deleting the comment: ' + str(e))
        
    if error_id:
        return redirect(url_for('error_comment', error_id=error_id))
    else:
        return redirect(url_for('index'))
    
@app.route('/add_rules_and_topics/<int:error_id>', methods=['GET', 'POST'])
def add_rules_and_topics(error_id):
    error = Error.query.get_or_404(error_id)
    topics = [error_topic.topic.id for error_topic in error.error_topics]
    rules = [error_rule.rule.id for error_rule in error.error_rules]
    all_topics = Topic.query.order_by(Topic.topic_name).all()
    all_rules = Rule.query.order_by(Rule.rule_name).all()
    rule_tags = [('', 'Select a Rule (optional)')] + [(rule.id, rule.rule_name) for rule in all_rules]    
    topic_tags = [('', 'Select a Topic (optional)')] + [(topic.id, topic.topic_name) for topic in all_topics]
    add_rules_and_topics_form = AddRulesAndTopicsForm()
    add_rules_and_topics_form.topic1.choices = topic_tags
    add_rules_and_topics_form.topic2.choices = topic_tags
    add_rules_and_topics_form.topic3.choices = topic_tags
    add_rules_and_topics_form.rule1.choices = rule_tags
    add_rules_and_topics_form.rule2.choices = rule_tags
    add_rules_and_topics_form.rule3.choices = rule_tags
    add_rules_and_topics_form.rule_topic1.choices = topic_tags
    add_rules_and_topics_form.rule_topic2.choices = topic_tags
    add_rules_and_topics_form.rule_topic3.choices = topic_tags
    

    if request.method == 'POST' and add_rules_and_topics_form.validate_on_submit():
        topics = []
        rules = []
        new_topic_name = None
        new_rule_name = None
        new_rule_text = None
        new_rule_topic_ids = []
        #Add topics:
        for i in range(1, 4):
            topic_id = request.form.get(f'topic{i}')
            if topic_id:
                topic = Topic.query.get(topic_id)
                if topic:
                    topics.append(topic.topic_name)
        #Add Rules:
        for i in range(1, 4):
            rule_id = request.form.get(f'rule{i}')
            if rule_id:
                rule = Rule.query.get(rule_id)
                if rule:
                    rules.append(rule.rule_name)
        #Define new topic:
        if request.form.get('new_topic_name'):
            existing_topic = Topic.query.filter_by(topic_name=request.form['new_topic_name']).first()
            if existing_topic:
                return 'This topic already exists.'
            else:
                new_topic_name = request.form['new_topic_name'].strip()
                if not new_topic_name:
                    new_topic_name = None
        #Define new rule:
        if request.form.get('new_rule_name'):
            existing_rule = Rule.query.filter_by(rule_name=request.form['new_rule_name']).first()
            if existing_rule:
                return 'This rule already exists.'
            else:
                new_rule_name = request.form['new_rule_name'].strip()
                new_rule_text = request.form['new_rule_text'].strip()
                if not new_rule_name:
                    new_rule_name = None
                if not new_rule_text:
                    new_rule_text = None
                for i in range(1, 4):
                    rule_topic_id = request.form.get(f'rule_topic{i}')
                    if rule_topic_id:
                        new_rule_topic_ids.append(rule_topic_id)
        # Log the values being passed to add_error for debugging
        print("Topics:", topics)
        print("Rules:", rules)
        print("New Topic Name:", new_topic_name)
        print("New Rule Name:", new_rule_name)
        print("New Rule Text:", new_rule_text)
        print("New Rule Topic IDs:", new_rule_topic_ids)
        add_rules_and_topics_handler(error_id, topics, rules, new_topic_name, new_rule_name,
                            new_rule_text, new_rule_topic_ids)   
    return render_template('add_rules_and_topics.html', error=error, add_rules_and_topics_form=add_rules_and_topics_form)


@app.route('/edit_rule/<int:rule_id>', methods=['GET', 'POST'])
def edit_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    rule_text = rule.rule_text
    all_topics = Topic.query.order_by(Topic.topic_name).all()
    topic_tags = [('', 'Select a Topic (optional)')] + [(topic.id, topic.topic_name) for topic in all_topics]
    edit_rule_form = EditRuleForm(rule_name=rule.rule_name,
                                  rule_text=rule_text)
    edit_rule_form.rule_topic1.choices = topic_tags
    edit_rule_form.rule_topic2.choices = topic_tags
    edit_rule_form.rule_topic3.choices = topic_tags    
    if request.method == 'POST' and edit_rule_form.validate_on_submit():
        rule.rule_name = request.form['rule_name']
        rule.rule_text = request.form['rule_text']
        rule.last_edited = datetime.now(timezone.utc)
        for i in range(1, 4):
            topic_id = request.form.get(f'rule_topic{i}')
            if topic_id:
                existing_rule_topic = RuleTopic.query.filter_by(rule_id=rule.id, topic_id=topic_id).first()
                if not existing_rule_topic:
                    new_rule_topic = RuleTopic(rule_id=rule.id, topic_id=topic_id)
                    db.session.add(new_rule_topic)
        try:
            db.session.commit()
            flash('Rule edited successfully.', category='success')
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}") 
        return redirect(url_for('edit_rule', rule_id=rule_id))   
    
    return render_template('edit_rule.html', rule=rule, edit_rule_form=edit_rule_form)

@app.route('/delete_error/<int:error_id>', methods=['GET', 'POST'])
def delete_error(error_id):
    error_to_delete = Error.query.filter_by(id=error_id).first()
    print('Error: ' + error_to_delete.incorrect_sentence)
    corrections_to_delete = Correction.query.filter_by(error_id=error_id).all()
    error_topics_to_delete = ErrorTopic.query.filter_by(error_id=error_id).all()
    error_rules_to_delete = ErrorRule.query.filter_by(error_id=error_id).all()
    list_items_to_delete = ListItem.query.filter_by(error_id=error_id).all()
    cloze_sentences_to_delete = ClozeSentence.query.filter_by(error_id=error_id).all()
    comments_to_delete = Comment.query.filter_by(error_id=error_id).all()
    db.session.delete(error_to_delete)    
    for correction in corrections_to_delete:
        db.session.delete(correction)
    for error_topic in error_topics_to_delete:
        db.session.delete(error_topic)
    for error_rule in error_rules_to_delete:
        db.session.delete(error_rule)
    for list_item in list_items_to_delete:
        db.session.delete(list_item)
    for cloze_sentence in cloze_sentences_to_delete:
        db.session.delete(cloze_sentence)
    for comment in comments_to_delete:
        db.session.delete(comment)
    try:
        db.session.commit()
        flash('Error deleted successfully.', category='success')
    except Exception as e:
        db.session.rollback()
        print('Error deleting the error: ' + str(e))
    return 'Error deleted successfully.'

@app.route('/remove_error_topic/<int:error_id>/<int:error_topic_id>', methods=['GET', 'POST'])
def remove_error_topic(error_id, error_topic_id):
    topic_to_remove = ErrorTopic.query.filter_by(id=error_topic_id).first()
    db.session.delete(topic_to_remove)
    try:
        db.session.commit()
        flash('Topic removed successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('edit', error_id=error_id))

@app.route('/remove_error_rule/<int:error_id>/<int:error_rule_id>', methods=['GET', 'POST'])
def remove_error_rule(error_id, error_rule_id):
    rule_to_remove = ErrorRule.query.filter_by(id=error_rule_id).first()
    db.session.delete(rule_to_remove)
    try:
        db.session.commit()
        flash('Rule removed successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('edit', error_id=error_id))

@app.route('/remove_rule_topic/<int:rule_id>/<int:rule_topic_id>', methods=['GET', 'POST'])
def remove_rule_topic(rule_id, rule_topic_id):
    rule_topic_to_remove = RuleTopic.query.filter_by(id=rule_topic_id).first()
    db.session.delete(rule_topic_to_remove)
    try:
        db.session.commit()
        flash('Topic removed successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('edit_rule', rule_id=rule_id))    

@app.route('/delete_topic/<int:topic_id>', methods=['GET', 'POST'])
def delete_topic(topic_id):
    topic_to_delete = Topic.query.filter_by(id=topic_id).first()
    db.session.delete(topic_to_delete)
    try:
        db.session.commit()
        flash('Topic deleted successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('topics'))

@app.route('/delete_rule/<int:rule_id>', methods=['GET', 'POST'])
def delete_rule(rule_id):
    rule_to_delete = Rule.query.filter_by(id=rule_id).first()
    db.session.delete(rule_to_delete)
    try:
        db.session.commit()
        flash('Rule deleted successfully.', category='success')
    except:
        db.session.rollback()
    return redirect(url_for('rules'))


@app.route('/display_by_topic', methods=['GET', 'POST'])
def display_by_topic():
    topic = None
    errors = db.session.query(Error).join(ErrorTopic).options(joinedload(Error.corrections))\
                        .order_by(desc(Error.entered)).limit(20).all()
    topics = Topic.query.order_by(Topic.topic_name).all()
    select_topic_form = SelectTopicForm()
    select_topic_form.selected_topic.choices = [('', 'Recent')] + [(topic.id, topic.topic_name) for topic in topics]
    if request.method == 'POST' and select_topic_form.validate():
        topic_id = select_topic_form.selected_topic.data
        topic = Topic.query.get(topic_id)
        if topic:
            errors = db.session.query(Error).join(ErrorTopic).options(joinedload(Error.corrections))\
                    .filter(ErrorTopic.topic_id==topic.id).order_by(desc(Error.id)).all()
    return render_template('display_by_topic.html', errors=errors, select_topic_form=select_topic_form, topic=topic)

@app.route('/topics')
def topics():
    topics = Topic.query.order_by(Topic.topic_name).all()
    edit_topic_form = EditTopicForm()
    add_topic_form = EditTopicForm()
    return render_template('topics.html', topics=topics, edit_topic_form=edit_topic_form, add_topic_form=add_topic_form)

@app.route('/add_topic', methods=['GET', 'POST'])
def add_topic():
    add_topic_form = EditTopicForm()
    if request.method == 'POST' and add_topic_form.validate_on_submit():
        topic_to_add = Topic(topic_name=request.form.get('topic_name'))
        db.session.add(topic_to_add)
        try:
            db.session.commit()
            flash('Topic added successfully.', category='success')
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
    return redirect(url_for('topics'))

@app.route('/edit_topic/<int:topic_id>', methods=['GET', 'POST'])
def edit_topic(topic_id):
    topic = Topic.query.filter_by(id=topic_id).first()
    edit_topic_form = EditTopicForm(topic_name=topic.topic_name)
    if request.method == 'POST' and edit_topic_form.validate_on_submit():
        topic.topic_name = request.form.get('topic_name')
        try:
            db.session.commit()
            flash('Topic edited successfully.', category='success')
        except:
            db.session.rollback()
        return redirect(url_for('topics'))

    

@app.route('/rules', methods=['GET', 'POST'])
def rules():
    all_topics = Topic.query.order_by(Topic.topic_name).all()
    topic_select_options = [('', 'Recent')] + [(topic.id, topic.topic_name) for topic in all_topics]
    select_topic_form = SelectTopicForm()
    select_topic_form.selected_topic.choices = topic_select_options
    topic = None
    rules = db.session.query(Rule).outerjoin(RuleTopic).order_by(desc(Rule.id)).limit(20).all()
    if request.method == 'POST' and select_topic_form.validate_on_submit():
        topic_id = select_topic_form.selected_topic.data
        topic = Topic.query.get(topic_id)
        if topic:
            rules = db.session.query(Rule).outerjoin(RuleTopic).filter(RuleTopic.topic_id==topic.id).order_by(desc(Rule.id)).all()
    return render_template('rules.html', rules=rules, topic=topic, select_topic_form=select_topic_form)

@app.route('/rule/<int:rule_id>', methods=['GET', 'POST'])
def rule(rule_id):
    rule = Rule.query.filter_by(id=rule_id).first()
    rule_errors = [rule_error.error for rule_error in rule.rule_errors]
    rule_topics = [rule_topic.topic for rule_topic in rule.rule_topics]
    rule_comments = [comment for comment in rule.comments]
    
    add_comment_form = AddCommentForm()
    
    if request.method == 'POST' and add_comment_form.validate_on_submit():
        new_comment = Comment(subject_heading=add_comment_form.subject_heading.data,
                              message=add_comment_form.message.data,
                              rule_id=rule.id)
        db.session.add(new_comment)
        try:
            db.session.commit()
            flash('Comment added successfully.', category='success')
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
    return render_template('rule.html', rule=rule, rule_topics=rule_topics, rule_errors=rule_errors, 
                           rule_comments=rule_comments, add_comment_form=add_comment_form)

@app.route('/parse_sentence/<int:error_id>')
def parse_sentence(error_id):
    error = Error.query.get(error_id)
    if error:
        correct_sentence = [correction.correct_sentence for correction in error.corrections][0]
        parsed_sentence = [token for token in parse_text(correct_sentence) if not token.is_punct]
        pos_explanations = [explain_pos_tag(token.pos_) for token in parsed_sentence if not token.is_punct]
        tag_explanations = [explain_pos_tag(token.tag_) for token in parsed_sentence if not token.is_punct]
        word_forms = get_word_forms(parsed_sentence)
        return render_template('parse_sentence.html', error=error, correct_sentence=correct_sentence, parsed_sentence=parsed_sentence,
                               pos_explanations=pos_explanations, tag_explanations=tag_explanations, word_forms=word_forms)
    else:
        return 'Error not found.'

if __name__ == '__main__':
    app.run(ssl_context=('certs/new_cert.pem', 'certs/new_key.pem'), debug=True)

#Running with SSL key:
#flask run --cert=certs/new_cert.pem --key=certs/new_key.pem