from flask import render_template, request, flash, redirect, url_for
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from app import app, login_required, teacher_required, current_user
from forms import *
from models import *
from errors import add_error


@app.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
@teacher_required
def teacher_dashboard():
    user = Teacher.query.get(current_user.id)
    all_topics = Topic.query.order_by(Topic.topic_name).all()
    all_rules = Rule.query.order_by(Rule.rule_name).all()
    topic_tags = [('', 'Select a Topic (optional)')] + [(topic.id, topic.topic_name) for topic in all_topics]
    rule_tags = [('', 'Select a Rule (optional)')] + [(rule.id, rule.rule_name) for rule in all_rules]

    add_form = AddForm(csrf_enabled=False)
    add_form.topic1.choices = topic_tags
    add_form.topic2.choices = topic_tags
    add_form.topic3.choices = topic_tags
    add_form.rule1.choices = rule_tags
    add_form.rule2.choices = rule_tags
    add_form.rule3.choices = rule_tags
    add_form.rule_topic1.choices = topic_tags
    add_form.rule_topic2.choices = topic_tags
    add_form.rule_topic3.choices = topic_tags
    
    #Select topic form:
    topic_select_options = [('', 'Recent')] + [(topic.id, topic.topic_name) for topic in all_topics]
    select_topic_form = SelectTopicForm(csrf_enabled=False)
    select_topic_form.selected_topic.choices = topic_select_options
    list_form = ManageListForm(csrf_enabled=False)
    existing_lists = List.query.all()
    list_form.existing_list.choices = [('', 'Add to an Existing List')] + [(list.id, list.list_name) for list in list(reversed(existing_lists))]
    
    #Process add form:
    if request.method == 'POST' and add_form.validate_on_submit():
        print('Form submitted')
        teacher_id = current_user.id
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
                    
                for i in range(1, 4):
                    rule_topic_id = request.form.get(f'rule_topic{i}')
                    if rule_topic_id:
                        new_rule_topic_ids.append(rule_topic_id)

        # Log the values being passed to add_error for debugging
        print("Teacher ID:", teacher_id)
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
        return redirect(url_for('teacher_dashboard'))

    topic = None
    errors = db.session.query(Error).filter(Error.teacher_id==current_user.id).outerjoin(ErrorTopic).options(joinedload(Error.corrections))\
            .order_by(desc(Error.entered)).limit(100).all()
    #Select topic form handling:
    if request.method == 'POST' and select_topic_form.validate_on_submit():
        topic_id = select_topic_form.selected_topic.data
        topic = Topic.query.get(topic_id)
        if topic:
            errors = db.session.query(Error).filter(Error.teacher_id==current_user.id).outerjoin(ErrorTopic).options(joinedload(Error.corrections))\
                    .filter(ErrorTopic.topic_id==topic.id).order_by(desc(Error.id)).all()
    return render_template('teacher_dashboard.html', errors=errors, add_form=add_form, list_form=list_form,
                            select_topic_form=select_topic_form, user=user)

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    user = Student.query.get(current_user.id)
    all_topics = Topic.query.order_by(Topic.topic_name).all()
    
    #Select topic form:
    topic_select_options = [('', 'Recent')] + [(topic.id, topic.topic_name) for topic in all_topics]
    select_topic_form = SelectTopicForm(csrf_enabled=False)
    select_topic_form.selected_topic.choices = topic_select_options
    list_form = ManageListForm(csrf_enabled=False)
    existing_lists = List.query.all()
    list_form.existing_list.choices = [('', 'Add to an Existing List')] + [(list.id, list.list_name) for list in list(reversed(existing_lists))]    
    
    topic = None
    errors = db.session.query(Error).outerjoin(ErrorTopic).options(joinedload(Error.corrections))\
            .order_by(desc(Error.entered)).limit(100).all()
    
    #Select topic form handling:
    if request.method == 'POST' and select_topic_form.validate_on_submit():
        topic_id = select_topic_form.selected_topic.data
        topic = Topic.query.get(topic_id)
        if topic:
            errors = db.session.query(Error).outerjoin(ErrorTopic).options(joinedload(Error.corrections))\
                    .filter(ErrorTopic.topic_id==topic.id).order_by(desc(Error.id)).all()
    return render_template('student_dashboard.html', errors=errors, list_form=list_form,
                            select_topic_form=select_topic_form, user=user) 
