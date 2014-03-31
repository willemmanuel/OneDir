from flask import Flask, url_for, render_template, request, redirect, flash, g, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from flask.ext.login import LoginManager, login_user , logout_user , current_user , login_required
import logging
import hashlib
from werkzeug.utils import secure_filename
import os
import datetime
# from sqlalchemy import create_engine
# from flask.ext.migrate import Migrate, MigrateCommand
# from flask.ext.script import Manager


#
#
# FLASK ONEDIR API
#
#

#
# GLOBAL VARIABLES
# Details the database, upload folders, and other configurations
#
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Will/test.db'
UPLOAD_FOLDER = '/Users/Will/Desktop/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# To do DB migration: uncomment this, then run
# python server.py db (migrate, then upgrade)
#
# migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)

#
# USER MODEL
# SQLAlchemy model that interacts with SQLite database
#
class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(10))
    email = db.Column('email',db.String(50),unique=True , index=True)
    files = relationship("File", backref="user")

    def __init__(self , username ,password , email):
        self.username = username
        self.password = hashlib.sha256(password).hexdigest()
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

    def get_folder(self):
        return app.config['UPLOAD_FOLDER'] + "/" + str(self.username)

class File(db.Model):
    __tablename__ = "files"
    username = db.Column('username',db.String(20), ForeignKey("users.username"))
    name = db.Column('name', db.String(30))
    path = db.Column('path', db.String(128))
    hash = db.Column('hash', db.String(40), primary_key=True)
    modified = db.Column('modified', db.DateTime)

    def __init__(self, username , name, path, hash, modified):
        self.username = username
        self.name = name
        self.path = path
        self.hash = hash
        self.modified = modified

    def relative_path(self):
        return self.path + "/" + self.name

    def absolute_path(self):
        user = User.query.filter_by(username=self.username).first()
        return str(user.get_folder()) + "/" + self.relative_path()

#
# LOGIN MANAGER - in charge of sessions
#
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=userid).first()

@app.errorhandler(404)
def not_found(error):
    return '{ "result" : -1, "msg" : "resource not found"}'

@login_manager.unauthorized_handler
def unauthorized():
    return '{ "result" : -2, "msg" : "unathorized"}'

@app.route('/list', methods=['GET'])
@login_required
def list():
    files = File.query.filter_by(username=current_user.username).all()
    if not files:
        return ""
    json_string = '{"files":['
    first = True
    for f in files:
        if not first:
            json_string += ","
        json_string += '{"username":"' + str(f.username) + '", "name":' + str(f.name) + '", "path":' +\
                       str(f.path) + '", "hash":' + str(f.hash) + '", "modified":' + str(f.modified) + '"}'
        first = False
    json_string += "]}"
    return json_string

@app.route('/delta', methods=['GET'])
@login_required
def delta():
    return "unimplemented"

@app.route('/file/<path:filename>', methods=['GET'])
@login_required
def get_file(filename):
    full_filename = os.path.join(current_user.get_folder(), filename)
    if not os.path.exists(full_filename):
        return '{ "result" : -1, "msg" : "file does not exist"}'
    else:
        with open(full_filename, "rb") as in_file:
            read = in_file.read()
        return read

@app.route('/file/<path:path>', methods=['POST'])
@login_required
def upload_file(path):
    file = request.files['file']
    if not is_safe(path):
        return '{ "result" : -1, "msg" : "unsafe path"}'
    if not file:
        return '{ "result" : -1, "msg" : "file not uploaded"}'
    filename = secure_filename(file.filename)
    full_path = os.path.join(current_user.get_folder(), path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    full_path = os.path.join(full_path, filename)
    file.save(full_path)
    file_hash = hash_file(full_path)
    entry = File(current_user.username, file.filename, path, file_hash, datetime.datetime.utcnow())
    dupe = File.query.filter_by(hash=file_hash, user=current_user).first()
    if dupe:
        dupe = entry
    else:
        db.session.add(entry)
    db.session.commit()
    return '{ "result" : 1, "msg" : "file uploaded"}'

@app.route('/file', methods=['POST'])
@login_required
def upload_no_path():
    file = request.files['file']
    if not file:
        return '{ "result" : -1, "msg" : "file not uploaded"}'
    filename = secure_filename(file.filename)
    full_path = os.path.join(current_user.get_folder(), filename)
    file.save(full_path)
    file_hash = hash_file(full_path)
    entry = File(current_user.username, file.filename, '/', file_hash, datetime.datetime.utcnow())
    dupe = File.query.filter_by(hash=file_hash, user=current_user).first()
    if dupe:
        dupe = entry
    else:
        db.session.add(entry)
    db.session.commit()
    return '{ "result" : 1, "msg" : "file uploaded"}'

@app.route('/register', methods=['POST'])
def register():
    username, password, email = str(request.json['username']), str(request.json['password']), str(request.json['email'])
    if not username or not password or not email:
        return '{ "result" : -1, "msg" : "missing parameters"}'
    try:
        user = User(username, password, email)
        db.session.add(user)
        db.session.commit()
        os.makedirs(user.get_folder())
    except:
        return '{ "result" : -1, "msg" : "registration failed"}'
    return '{ "result" :"' + str(username) + '", "msg" : "user created"}'

@app.route('/session', methods=['POST'])
def login():
    if not request.json['username'] or not request.json['password']:
        return '{ "result" : -1, "msg" : "missing parameters"}'
    username = request.json['username']
    password = request.json['password']
    hash = hashlib.sha256(password).hexdigest()
    registered_user = User.query.filter_by(username=username,password=hash).first()
    if registered_user is None:
        return '{ "result" : -1, "msg" : "login failed"}'
    login_user(registered_user)
    return '{ "result" : "' + str(username) + '", "msg" : "authenticated"}'

@app.route('/session', methods=['DELETE'])
def logout():
    if current_user:
            r = '{ "result" : "' + str(current_user.username) + '", "msg" : "logged out"}'
            logout_user()
    else:
        r = '{ "result" : -1, "msg" : "not logged in"}'
    return r

def is_safe(filename):
    here = os.path.abspath(".")
    there = os.path.abspath(filename)
    return there.startswith(here)

def hash_file(path):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.sha1(data + str(os.stat(path).st_size) + str(current_user.username)).hexdigest()

if __name__ == '__main__':
    # manager.run()
    logging.basicConfig(level=logging.DEBUG)
    app.run(threaded=True)