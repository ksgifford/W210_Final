from flask import render_template, flash, redirect, url_for, request, send_file
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm
import boto3
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
import csv
import shutil
import requests
import json
import os

s3_client = boto3.client('s3')
bucket_name = 'w210-img-upload'

s3_resource = boto3.resource('s3')
my_bucket = s3_resource.Bucket(bucket_name)

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
            s3_client.upload_fileobj(data_file, bucket_name, current_user.username+'/upload/'+data_file.filename)
            print("Uploading "+data_file.filename+" to "+bucket_name+".")

        return redirect(url_for('complete'))
    else:
        username = current_user.username
        return render_template('upload.html', title='File Upload', username = username)

@app.route('/complete', methods=['GET', 'POST'])
@login_required
def complete():
    # bucket_url = 'https://s3.console.aws.amazon.com/s3/buckets/'+bucket_name

    if request.method == "POST":
        if 'upload_again' in request.form:
            return redirect(url_for('upload'))
        elif 'launcher' in request.form:
            return redirect(url_for('classify'))
    else:
        return render_template('complete.html', title='Thank You!')

@app.route('/output')
@login_required
def output():
    file_prefix = current_user.username+'/wtf'
    file_list = list(my_bucket.objects.filter(Prefix=file_prefix))[1:]
    img_dir = './app/downloads/'+current_user.username+'/img'
    for obj in file_list:
        local_file_name = './app/downloads/'+current_user.username+'/img/'+obj.key.split('/')[2]
        my_bucket.download_file(obj.key,local_file_name)

    shutil.make_archive('./app/downloads/'+current_user.username+'/'+current_user.username+'_WTFimages','zip',img_dir)
    for file in os.listdir(img_dir):
        file_path = os.path.join(img_dir,file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(e)

    return render_template('output.html', title='Results Download')

@app.route('/classify')
@login_required
def classify():
    path = '/home/ubuntu/w210-img-upload/'+current_user.username+'/upload'
    username = current_user.username
    payload = json.dumps({'path':path, 'userId':username})
    req = requests.post("http://ec2-3-87-218-106.compute-1.amazonaws.com:5000/predictFolder", json=payload)

    test_file = './app/downloads/'+current_user.username+'/'+current_user.username+'TEST.txt'
    with open(test_file, 'w') as json_file:
        json.dump(req.text, json_file)

    return redirect(url_for('output'))

@app.route('/csv_download')
@login_required
def csv_download():
    db_string = "postgres://dbmaster:dbpa$$w0rd!@w210postgres01.c8siy60gz3hg.us-east-1.rds.amazonaws.com:5432/w210results"
    engine = create_engine(db_string, echo=True)
    Base = declarative_base(engine)

    output_file = './app/downloads/'+current_user.username+'/'+current_user.username+'_results.csv'

    class Results(Base):
        __tablename__ = 'test_upload'
        # __tablename__ = 'dummy_table'
        # __tablename__ = str(current_user.username + '_results')
        __table_args__ = {'autoload':True}

    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()

    qry = session.query(Results)

    with open(output_file, 'w') as csvfile:
        outcsv = csv.writer(csvfile, delimiter=',',quotechar='"', quoting = csv.QUOTE_MINIMAL)
        header = Results.__table__.columns.keys()

        outcsv.writerow(header)

        for record in qry.all():
            outcsv.writerow([getattr(record, c) for c in header ])

    session.close()
    engine.dispose()

    download_file = current_user.username+'_results.csv'
    return send_file('./downloads/'+current_user.username+'/'+download_file, attachment_filename=download_file)
    # return send_file(output_file, attachment_filename=download_file)

@app.route('/zip_download')
@login_required
def zip_download():
    download_zip = current_user.username+'_WTFimages.zip'
    return send_file('./downloads/'+current_user.username+'/'+download_zip, attachment_filename=download_zip)
