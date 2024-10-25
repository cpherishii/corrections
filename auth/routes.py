from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from . import auth
from app import app
from extensions import db
from models import Teacher, Student
from forms import LoginForm, RegistrationForm

#Register as a teacher:
@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    registration_form = RegistrationForm()
    if request.method == 'POST' and registration_form.validate_on_submit():
        teacher = Teacher(username=registration_form.username.data, email=registration_form.email.data)
        teacher.set_password(registration_form.password.data)
        db.session.add(teacher)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}") 
        return redirect(url_for('login_teacher'))
    return render_template('register_teacher.html', registration_form=registration_form)

#Register as a student:
@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    registration_form = RegistrationForm()
    if request.method == 'POST' and registration_form.validate_on_submit():
        student = Student(username=registration_form.username.data, email=registration_form.email.data)
        student.set_password(registration_form.password.data)
        db.session.add(student)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}") 
        return redirect(url_for('login_student'))
    return render_template('register_student.html', registration_form=registration_form)

#Log in as a teacher:
@app.route('/login_teacher', methods=['GET', 'POST'])
def login_teacher():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    if request.method == 'POST' and login_form.validate_on_submit():
        user = Teacher.query.filter_by(email=login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            flash(f'Welcome, {current_user.username}!')
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('login_teacher', _external=True, _scheme='https'))
    return render_template('login_teacher.html', login_form=login_form)

#Login as a student:
@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    if request.method == 'POST' and login_form.validate_on_submit():
        user = Student.query.filter_by(email=login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            flash(f'Welcome, {current_user.username}!')
            return redirect(url_for('student_dashboard'))
        else:
            return redirect(url_for('login_student', _external=True, _scheme='https'))
    return render_template('login_student.html', login_form=login_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))