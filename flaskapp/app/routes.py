from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm
import boto3
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

s3 = boto3.client('s3')
bucket_name = 'w210-img-upload'

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('upload')
        return redirect(next_page)
    return render_template('index.html', title='Home', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        data_files = request.files.getlist('file[]')
        for data_file in data_files:
            # print(data_file)
            s3.upload_fileobj(data_file, bucket_name, current_user.username+'/upload/'+data_file.filename)
            print("Uploading "+data_file.filename+" to "+bucket_name+".")

        return redirect(url_for('complete'))
    else:
        return render_template('upload.html', title='File Upload')

@app.route('/complete')
@login_required
def complete():
    bucket_url = 'https://s3.console.aws.amazon.com/s3/buckets/'+bucket_name
    return render_template('complete.html', title='Thank You!', bucket_url = bucket_url)
