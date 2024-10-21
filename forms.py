from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, \
                    SelectMultipleField, RadioField, BooleanField, PasswordField, widgets, HiddenField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Optional
from email_validator import validate_email, EmailNotValidError

class RegistrationForm(FlaskForm):
    user_type = RadioField('Student or Teacher?', choices=[(1, 'Student'), (2, 'Teacher')], default=1)
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    user_type = RadioField('Student or Teacher?', choices=[(1, 'Student'), (2, 'Teacher')], default=1)
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')


class AddForm(FlaskForm):
    error = StringField('Error:', validators=[DataRequired()])
    correction = TextAreaField('Correction:', validators=[DataRequired()])
    topic1 = SelectField('Add Topic:', choices=[])
    topic2 = SelectField('Add Topic:', choices=[])
    topic3 = SelectField('Add Topic:', choices=[])
    rule1 = SelectField('Add Rule', choices=[])
    rule2 = SelectField('Add Rule', choices=[])
    rule3 = SelectField('Add Rule', choices=[])
    #Define new topic:
    new_topic_name = StringField('New Topic Name:')
    #Define new rule:
    new_rule_name = StringField('New Rule Name:')
    new_rule_text = TextAreaField('Explanation:')
    rule_topic1 = SelectField('Add Topic:', choices=[])
    rule_topic2 = SelectField('Add Topic:', choices=[])
    rule_topic3 = SelectField('Add Topic:', choices=[])
    submit = SubmitField("Add Sentence")
   

class EditForm(FlaskForm):
    error = StringField("Error:", validators=[DataRequired()])
    correction = TextAreaField("Correction:", validators=[DataRequired()])
    topic1 = SelectField('Add Topic:', choices=[])
    topic2 = SelectField('Add Topic:', choices=[])
    topic3 = SelectField('Add Topic:', choices=[])
    rule1 = SelectField('Add Rule', choices=[])
    rule2 = SelectField('Add Rule', choices=[])
    rule3 = SelectField('Add Rule', choices=[])
    #Define new topic:
    new_topic_name = StringField('New Topic Name:')
    #Define new rule:
    new_rule_name = StringField('New Rule Name:')
    new_rule_text = TextAreaField('Explanation:')
    rule_topic1 = SelectField('Add Topic:', choices=[])
    rule_topic2 = SelectField('Add Topic:', choices=[])
    rule_topic3 = SelectField('Add Topic:', choices=[])
    submit = SubmitField("Change Sentences")

    def __init__(self, error=None, correction=None, topics=None, rules=None, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        if error:
            self.error.data = error
        if correction:
            self.correction.data = correction
        if topics:
            self.topic1.data = topics[0] if len(topics) > 0 else ''
            self.topic2.data = topics[1] if len(topics) > 1 else ''
            self.topic3.data = topics[2] if len(topics) > 2 else ''
        if rules:
            self.rule1.data = rules[0] if len(rules) > 0 else ''
            self.rule2.data = rules[1] if len(rules) > 1 else ''
            self.rule3.data = rules[2] if len(rules) > 2 else ''

class RemoveForm(FlaskForm):
    submit = SubmitField("Remove")

class SelectTopicForm(FlaskForm):
    selected_topic = SelectField('Topic:', choices = [])
    submit = SubmitField('Submit')

class EditTopicForm(FlaskForm):
    topic_name = StringField('Topic Name:', validators=[DataRequired()])
    submit = SubmitField('Change Topic Name')

class EditRuleForm(FlaskForm):
    rule_name = StringField('Rule Name:', validators=[DataRequired()])
    rule_text = TextAreaField('Explanation:', validators=[DataRequired()])
    rule_topic1 = SelectField('Add Topic:', choices=[])
    rule_topic2 = SelectField('Add Topic:', choices=[])
    rule_topic3 = SelectField('Add Topic:', choices=[])
    submit = SubmitField('Change Rule')
    #def __init__(self, rule_name=None, rule_text=None, rule_topics=None, *args, **kwargs):
    #    super(EditRuleForm, self).__init__(*args, **kwargs)
    #    if rule_name:
    #        self.rule_name.data = rule_name
    #    if rule_text:
    #        self.rule_text.data = rule_text
    #    if rule_topics:
    #        self.rule_topic1.data = rule_topics[0] if len(topics) > 0 else ''
    #        self.rule_topic2.data = rule_topics[1] if len(topics) > 1 else ''
    #        self.rule_topic3.data = rule_topics[2] if len(topics) > 2 else ''

class EditListForm(FlaskForm):
    list_name = StringField('List Name:')
    submit = SubmitField('Change List Name')
    
class ManageListForm(FlaskForm):
    existing_list = SelectField('Existing List', choices=[], validators=[Optional()])
    new_list_name = StringField('New List', validators=[Optional()])
    submit = SubmitField('Add to List')

class AddRulesAndTopicsForm(FlaskForm):
    topic1 = SelectField('Add Topic:', choices=[])
    topic2 = SelectField('Add Topic:', choices=[])
    topic3 = SelectField('Add Topic:', choices=[])
    rule1 = SelectField('Add Rule', choices=[])
    rule2 = SelectField('Add Rule', choices=[])
    rule3 = SelectField('Add Rule', choices=[])
    #Define new topic:
    new_topic_name = StringField('New Topic Name:')
    #Define new rule:
    new_rule_name = StringField('New Rule Name:')
    new_rule_text = TextAreaField('Explanation:')
    rule_topic1 = SelectField('Add Topic:', choices=[])
    rule_topic2 = SelectField('Add Topic:', choices=[])
    rule_topic3 = SelectField('Add Topic:', choices=[])
    submit = SubmitField("Add")

    def __init__(self, topics=None, rules=None, *args, **kwargs):
        super(AddRulesAndTopicsForm, self).__init__(*args, **kwargs)
        if topics:
            self.topic1.data = topics[0] if len(topics) > 0 else ''
            self.topic2.data = topics[1] if len(topics) > 1 else ''
            self.topic3.data = topics[2] if len(topics) > 2 else ''
        if rules:
            self.rule1.data = rules[0] if len(rules) > 0 else ''
            self.rule2.data = rules[1] if len(rules) > 1 else ''
            self.rule3.data = rules[2] if len(rules) > 2 else ''

class SelectErrorsForm(FlaskForm):
    selected_errors = SelectMultipleField(choices=[], validators=[DataRequired()])
    submit = SubmitField('Display List')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ErrorExerciseForm(FlaskForm):
    list_name = StringField('List Name (optional):')
    existing_list = SelectField('Choose an existing list:', choices = [])
    exercise = RadioField('Choose an exercise:', choices=[(1, 'Correct or Incorrect?'), 
                                                          (2, 'Choose the Correct Sentence'),
                                                          (3, 'Correct the Sentence'),
                                                          (4, 'Mix it up!')],
                                                           default='1', validators=[DataRequired()])
    topics = MultiCheckboxField('Select topics to practice:', choices=[])
    submit = SubmitField('Let\'s Go!')

class ClozeExerciseForm(FlaskForm):
    list_name = StringField('List Name (optional):')
    target_words = TextAreaField('Words to Practise:')
    existing_list = SelectField('Choose an existing list:', choices = [])
    submit = SubmitField('Let\'s Go!')

class VerbFormExerciseForm(FlaskForm):
    verb_forms = RadioField('Verb forms to practise:', choices = [
        ('gerund_infinitive', 'Gerund (ing) or "to" + Infinitive'),
        ('subject_verb', 'Subject-Verb Agreement (he/she/it vs I/you/we/they)'),
        ('all_forms', 'All forms')
    ], validators=[DataRequired()], default='gerund_infinitive')
    num_sentences = IntegerField('Number of sentences:', default = 50, validators=[DataRequired()])
    submit = SubmitField('Let\'s Go!')
    
class EditClozeSentenceForm(FlaskForm):
    clozed_sentence = StringField('Cloze Sentence:')
    original_sentences = TextAreaField('Original Sentences:', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class WorksheetForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    worksheet_type = RadioField('Type of Worksheet', choices=[(1, 'Individual'),
                                                             (2, 'Student A / Student B')],
                                                             default='1', validators=[DataRequired()])
    exercise = RadioField('Exercise', choices=[(1, 'Correct or Incorrect?'), 
                                                    (2, 'Choose the Correct Sentence'),
                                                    (3, 'Correct the Sentence')],
                                                     default='1')
    number_of_questions = IntegerField('Number of Questions')
    randomize = BooleanField('Randomize?')
    submit = SubmitField('Create Worksheet')
    
class AddCommentForm(FlaskForm):
    subject_heading = StringField('Subject Heading (optional):')
    message = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')