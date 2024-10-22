from extensions import db
from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_migrate import Migrate

migrate = Migrate(app, db)

class Teacher(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    is_admin = db.Column(db.Boolean, default = False)
    username = db.Column(db.String(75), index = True, unique = True, nullable = False)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(150), nullable = False)
    joined = db.Column(db.DateTime(), default = datetime.now(timezone.utc), nullable = False)
    errors = db.relationship('Error', backref = 'teacher', lazy = 'joined')
    lists = db.relationship('List', backref = 'teacher', lazy = 'joined', cascade = 'all, delete-orphan')
    cloze_lists = db.relationship('ClozeList', backref = 'teacher', lazy = 'joined', cascade = 'all, delete-orphan')
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return f'teacher:{self.id}'


class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(75), index = True, unique = True, nullable = False)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(150), nullable = False)
    joined = db.Column(db.DateTime(), default = datetime.now(timezone.utc), nullable = False)
    errors = db.relationship('Error', backref = 'student', lazy = 'joined')    
    lists = db.relationship('List', backref = 'student', lazy = 'joined', cascade = 'all, delete-orphan')    
    cloze_lists = db.relationship('ClozeList', backref = 'student', lazy = 'joined', cascade = 'all, delete-orphan')
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return f'student:{self.id}'

class Error(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    incorrect_sentence = db.Column(db.String(300), index = True, unique = True, nullable = False)
    corrections = db.relationship('Correction', backref = 'error', lazy = 'joined', cascade = 'all, delete-orphan')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    error_topics = db.relationship('ErrorTopic', backref = 'error', lazy = 'joined', cascade = 'all, delete-orphan')
    error_rules = db.relationship('ErrorRule', backref = 'error', lazy = 'joined', cascade = 'all, delete-orphan')
    entered = db.Column(db.DateTime, default = datetime.now(timezone.utc), nullable=False)
    last_edited = db.Column(db.DateTime, default = datetime.now(timezone.utc), nullable=False)
    list_items = db.relationship('ListItem', backref = 'error', lazy = 'joined')
    cloze_sentences = db.relationship('ClozeSentence', backref = 'error', lazy = 'joined')
    comments = db.relationship('Comment', backref = 'error', lazy = 'joined', cascade = 'all, delete-orphan')

class Correction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    correct_sentence = db.Column(db.String(300), index = True, unique = False, nullable = False)
    error_id = db.Column(db.Integer, db.ForeignKey('error.id', ondelete = 'CASCADE'), nullable = False)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    topic_name = db.Column(db.String(200), index = True, unique = True, nullable = False)
    topic_errors = db.relationship('ErrorTopic', backref = "topic", lazy = 'joined', cascade = 'all, delete-orphan')
    topic_rules = db.relationship('RuleTopic', backref = 'topic', lazy = 'joined', cascade = 'all, delete-orphan')

class ErrorTopic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    error_id = db.Column(db.Integer, db.ForeignKey('error.id', ondelete = 'CASCADE'), nullable = False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id', ondelete = 'CASCADE'), nullable = False)

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    rule_name = db.Column(db.String(200), index = True, unique = True, nullable = False)
    rule_text = db.Column(db.Text, index = False, unique = True)
    examples = db.relationship('Example', backref = 'rule', lazy = 'joined', cascade = 'all, delete-orphan')
    rule_topics = db.relationship('RuleTopic', backref = 'rule', lazy = 'joined', cascade = 'all, delete-orphan')
    rule_errors = db.relationship('ErrorRule', backref = 'rule', lazy = 'joined', cascade = 'all, delete-orphan')
    entered = db.Column(db.DateTime, default = datetime.now(timezone.utc), nullable=False)
    last_edited = db.Column(db.DateTime, default = datetime.now(timezone.utc), nullable=False)
    comments = db.relationship('Comment', backref = 'rule', lazy = 'joined', cascade = 'all, delete-orphan')

class Example(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    example_text = db.Column(db.String(200), index = True, unique = True, nullable = False)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id', ondelete = 'CASCADE'), nullable = False)

class RuleTopic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id', ondelete = 'CASCADE'), nullable = False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id', ondelete = 'CASCADE'), nullable = False)

class ErrorRule(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    error_id = db.Column(db.Integer, db.ForeignKey('error.id', ondelete = 'CASCADE'), nullable = False)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id', ondelete = 'CASCADE'), nullable = False)

class List(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    list_name = db.Column(db.String(100), index = True, nullable = False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id', ondelete = 'CASCADE'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete = 'CASCADE'))
    list_items = db.relationship('ListItem', backref = 'list', lazy = 'joined', cascade = 'all, delete-orphan')

class ListItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    error_id = db.Column(db.Integer, db.ForeignKey('error.id', ondelete = 'CASCADE'), nullable = False)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id', ondelete = 'CASCADE'), nullable = False)

class ClozeList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    list_name = db.Column(db.String(100), index = True, nullable = False)
    cloze_sentences = db.relationship('ClozeSentence', backref='cloze_list', lazy='joined', cascade = 'all, delete-orphan')
    target_words = db.Column(db.String, nullable = False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id', ondelete = 'CASCADE'), nullable = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete = 'CASCADE'), nullable = True)

class ClozeSentence(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    original_sentences = db.Column(db.Text, index = True, nullable = False)
    clozed_sentence = db.Column(db.String, nullable = False)
    missing_words = db.Column(db.String, nullable = False)
    cloze_list_id = db.Column(db.Integer, db.ForeignKey('cloze_list.id', ondelete = 'CASCADE'))
    error_id = db.Column(db.Integer, db.ForeignKey('error.id'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subject_heading = db.Column(db.String(150))
    message = db.Column(db.Text, nullable = False)
    error_id = db.Column(db.Integer, db.ForeignKey('error.id'))
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'))