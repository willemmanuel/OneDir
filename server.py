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
from logging.handlers import RotatingFileHandler
import shutil
from os.path import isdir
from sqlalchemy import create_engine
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Will's settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Will/test.db'
UPLOAD_FOLDER = '/Users/Will/Desktop/uploads'
#Chris's settings
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/christopher/serverside/test.db'
# UPLOAD_FOLDER = '/home/christopher/serverside/onedir'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# To do DB migration: uncomment this, then run
# python server.py db (migrate, then upgrade)
# #
# migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)

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
    username = db.Column('username',db.String(20), ForeignKey("users.username"), primary_key=True)
    name = db.Column('name', db.String(30), primary_key=True)
    path = db.Column('path', db.String(128), primary_key=True)
    hash = db.Column('hash', db.String(40))
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

class FileShare(db.Model):
    __tablename__ = 'fileshares'
    shared_by = db.Column('shared_by',db.String(20), ForeignKey("users.username"), primary_key=True)
    shared_with = db.Column('shared_with',db.String(20), ForeignKey("users.username"), primary_key=True)
    name = db.Column('name', db.String(30), primary_key=True)
    path = db.Column('path', db.String(128), primary_key=True)

    def __init__(self, shared_by , shared_with, name, path):
        self.shared_by = shared_by
        self.shared_with = shared_with
        self.name = name
        self.path = path

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=userid).first()

@app.errorhandler(404)
def not_found(error):
    app.logger.info('User 404\'d at ' + str(datetime.datetime.utcnow()))
    return '{ "result" : -1, "msg" : "resource not found"}'

@login_manager.unauthorized_handler
def unauthorized():
    app.logger.info('Unauthorized resource access attempted at ' + str(datetime.datetime.utcnow()))
    return '{ "result" : -2, "msg" : "unathorized"}'

@app.route('/list', methods=['GET'])
@login_required
def list():
    app.logger.info(current_user.username + " asked for a list of all files at " + str(datetime.datetime.utcnow()))
    files = File.query.filter_by(username=current_user.username).all()
    if not files:
        return ""
    json_string = '{"files":['
    first = True
    for f in files:
        if not first:
            json_string += ","
        json_string += '{"username":"' + str(f.username) + '", "name":"' + str(f.name) + '", "path":"' +\
                       str(f.path) + '", "hash":"' + str(f.hash) + '", "modified":"' + str(f.modified) + '"}'
        first = False
    json_string += "]}"
    return json_string

@app.route('/share/list', methods=['GET'])
@login_required
def get_shared_list():
    app.logger.info(current_user.username + " asked for a list of shared files at " + str(datetime.datetime.utcnow()))
    shared = FileShare.query.filter_by(shared_with=current_user.username).all()
    if not shared:
        return ""
    json_string = '{"files":['
    first = True
    for s in shared:
        f = File.query.filter_by(username=s.shared_by, name=s.name, path=sanitize_path(s.path)).first()
        if not first:
            json_string += ","
        json_string += '{"username":"' + str(f.username) + '", "name":"' + str(f.name) + '", "path":"' +\
                       str(f.path) + '", "hash":"' + str(f.hash) + '", "modified":"' + str(f.modified) + '"}'
        first = False
    json_string += "]}"
    return json_string

@app.route('/share', methods=['GET'])
@login_required
def get_shared_file():
    username, name, path = str(request.json['username']), str(request.json['name']), sanitize_path(str(request.json['path']))
    s = FileShare.query.filter_by(shared_by=username, name=name, path=path).first()
    if not s:
        return '{ "result" : -1, "msg" : "file not shared"}'
    full_filename = app.config['UPLOAD_FOLDER'] + "/" + username
    full_filename = os.path.join(full_filename, path)
    full_filename = os.path.join(full_filename, name)
    app.logger.info("serving " + current_user.username + full_filename + " at " + str(datetime.datetime.utcnow()))
    if not os.path.exists(full_filename):
        return '{ "result" : -1, "msg" : "file does not exist"}'
    else:
        with open(full_filename, "rb") as in_file:
            read = in_file.read()
        return read

@app.route('/share', methods=['POST'])
@login_required
def add_shared_file():
    username, name, path = str(request.json['username']), str(request.json['name']), sanitize_path(str(request.json['path']))
    app.logger.info(current_user.username + " sharing file with " + username + " at " + str(datetime.datetime.utcnow()))
    share = FileShare(current_user.username, username, name, path)
    db.session.add(share)
    try:
        db.session.commit()
        return '{ "result" : 1, "msg" : "file shared"}'
    except:
        return '{ "result" : -1, "msg" : "file not shared"}'

@app.route('/share', methods=['DELETE'])
@login_required
def remove_shared_file():
    username, name, path = str(request.json['username']), str(request.json['file']), sanitize_path(str(request.json['path']))
    app.logger.info(current_user.username + " unsharing file with " + username + " at " + str(datetime.datetime.utcnow()))
    share = FileShare(current_user.username, username, name, path)
    db.session.delete(share)
    try:
        db.session.commit()
        return '{ "result" : 1, "msg" : "file shared"}'
    except:
        return '{ "result" : -1, "msg" : "file not shared"}'

@app.route('/admin/list', methods=['GET'])
@login_required
def admin_list():
    app.logger.info("admin asked for a list of all files at " + str(datetime.datetime.utcnow()))
    if current_user.username != 'admin':
        return '{ "result" : -2, "msg" : "unathorized"}'
    files = File.query.all()
    if not files:
        return ""
    json_string = '{"files":['
    first = True
    for f in files:
        if not first:
            json_string += ","
        json_string += '{"username":"' + str(f.username) + '", "name":"' + str(f.name) + '", "path":"' +\
                       str(f.path) + '", "hash":"' + str(f.hash) + '", "modified":"' + str(f.modified) + '"}'
        first = False
    json_string += "]}"
    return json_string

@app.route('/file/<path:filename>', methods=['GET'])
@login_required
def get_file(filename):
    full_filename = os.path.join(current_user.get_folder(), filename)
    app.logger.info("serving " + current_user.username + full_filename + " at " + str(datetime.datetime.utcnow()))
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
    if file.filename.startswith('.'):
        return '{ "result" : -1, "msg" : ". files not accepted"}'
    if path.startswith('shared/'):
        return '{ "result" : 1, "msg" : "skipping shared files"}'
    filename = secure_filename(file.filename)
    app.logger.info(current_user.username + " is uploading " + filename + " at " + str(datetime.datetime.utcnow()))
    full_path = os.path.join(current_user.get_folder(), path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    full_path = os.path.join(full_path, filename)
    file.save(full_path)
    file_hash = hash_file(full_path)
    entry = File(current_user.username, file.filename, path, file_hash, datetime.datetime.utcnow())
    dupe = File.query.filter_by(user=current_user, path=sanitize_path(path), name=filename).first()
    if dupe:
        db.session.delete(dupe)
    db.session.add(entry)
    db.session.commit()
    return '{ "result" : 1, "msg" : "file uploaded"}'

@app.route('/file', methods=['DELETE'])
@login_required
def delete():
    file = request.json['file']
    path = request.json['path']
    app.logger.info(current_user.username + " is deleting " + file + " at " + str(datetime.datetime.utcnow()))
    if not file:
        return '{ "result" : -1, "msg" : "missing parameters"}'
    fixed_path = sanitize_path(request.json['path'])
    file = secure_filename(file)
    full_path = os.path.join(current_user.get_folder(), fixed_path)
    full_path = os.path.join(full_path, file)
    if not os.path.exists(full_path):
        return '{ "result" : -1, "msg" : "file does not exist"}'
    entry = File.query.filter_by(path=sanitize_path(path), name=file, user=current_user).filter().first()
    if entry:
        db.session.delete(entry)
    db.session.commit()
    try:
        os.remove(full_path)
    except:
        return '{ "result" : 1, "msg" : "delete failed"}'
    return '{ "result" : 1, "msg" : "file deleted"}'

@app.route('/admin/file', methods=['DELETE'])
@login_required
def admin_delete():
    if str(current_user.username) != 'admin':
        return '{ "result" : -2, "msg" : "unathorized"}'
    file = request.json['file']
    path = request.json['path']
    user = request.json['user']
    app.logger.info("admin is deleting " + file + " owned by " + user + " at " + str(datetime.datetime.utcnow()))
    if not file:
        return '{ "result" : -1, "msg" : "missing parameters"}'
    fixed_path = sanitize_path(request.json['path'])
    file = secure_filename(file)
    full_path = os.path.join(app.config['UPLOAD_FOLDER'] + "/" + str(user), fixed_path)
    full_path = os.path.join(full_path, file)
    if not os.path.exists(full_path):
        return '{ "result" : -1, "msg" : "file does not exist"}'
    user = User.query.filter_by(username=user).first()
    entry = File.query.filter_by(path=sanitize_path(path), name=file, user=user).filter().first()
    if entry:
        db.session.delete(entry)
    db.session.commit()
    try:
        os.remove(full_path)
    except:
        return '{ "result" : 1, "msg" : "delete failed"}'
    return '{ "result" : 1, "msg" : "file deleted"}'

@app.route('/file', methods=['POST'])
@login_required
def upload_no_path():
    file = request.files['file']
    if not file:
        return '{ "result" : -1, "msg" : "file not uploaded"}'
    filename = secure_filename(file.filename)
    app.logger.info(current_user.username + " is uploading " + filename + " at " + str(datetime.datetime.utcnow()))
    full_path = os.path.join(current_user.get_folder(), filename)
    file.save(full_path)
    file_hash = hash_file(full_path)
    entry = File(current_user.username, file.filename, '', file_hash, datetime.datetime.utcnow())
    dupe = File.query.filter_by(user=current_user, path='', name=filename).first()
    if dupe:
        db.session.delete(dupe)
    db.session.add(entry)
    db.session.commit()
    return '{ "result" : 1, "msg" : "file uploaded"}'

@app.route('/register', methods=['POST'])
def register():
    username, password, email = str(request.json['username']), str(request.json['password']), str(request.json['email'])
    app.logger.info(username + " registered at " + str(datetime.datetime.utcnow()))
    if not username or not password or not email:
        return '{ "result" : -1, "msg" : "missing parameters"}'
    try:
        user = User(username, password, email)
        db.session.add(user)
        db.session.commit()
        #does it check to see if user exists first?
        #if isdir(user.get_folder()):
        #    shutil.rmtree(user.get_folder())
        os.makedirs(user.get_folder())
    except Exception as e:
        print e
        return '{ "result" : -1, "msg" : "registration failed"}'
    return '{ "result" :"' + str(username) + '", "msg" : "user created"}'

@app.route('/session', methods=['POST'])
def login():
    if not request.json['username'] or not request.json['password']:
        return '{ "result" : -1, "msg" : "missing parameters"}'
    username = request.json['username']
    password = request.json['password']
    app.logger.info(username + " logged in at " + str(datetime.datetime.utcnow()))
    hash = hashlib.sha256(password).hexdigest()
    registered_user = User.query.filter_by(username=username,password=hash).first()
    if registered_user is None:
        return '{ "result" : -1, "msg" : "login failed"}'
    login_user(registered_user)
    return '{ "result" : "' + str(username) + '", "msg" : "authenticated"}'

@app.route('/change_password', methods=['PUT'])
@login_required
def change_password():
    if not request.json['password']:
        return '{ "result" : -1, "msg" : "missing parameters"}'
    password = request.json['password']
    app.logger.info(current_user.username + " changed password at " + str(datetime.datetime.utcnow()))
    hash = hashlib.sha256(password).hexdigest()
    current_user.password = hash
    db.session.commit()
    logout_user()
    return '{ "result" : "1", "msg" : "changed password"}'

@app.route('/admin/change_password', methods=['PUT'])
@login_required
def admin_change_password():
    if current_user.username != 'admin':
        return '{ "result" : "-2", "msg" : "unauthorized"}'
    if not request.json['password'] or not request.json['user']:
        return '{ "result" : -1, "msg" : "missing parameters"}'
    password = request.json['password']
    user = request.json['user']
    app.logger.info("admin changed " + user + "'s password at " + str(datetime.datetime.utcnow()))
    hash = hashlib.sha256(password).hexdigest()
    user = User.query.filter_by(username=user).first()
    user.password = hash
    db.session.commit()
    return '{ "result" : "1", "msg" : "changed password"}'

@app.route('/file', methods=['PUT'])
@login_required
def update():
    # {'op': 'rename or move', 'old_file/path:','new_file/path', 'file/path'}
    if request.json['op'] == 'rename':
        old_file = secure_filename(request.json['old_file'])
        new_file = secure_filename(request.json['new_file'])
        path = sanitize_path(request.json['path'])
        app.logger.info(current_user.username + " renamed "+ old_file + " at " + str(datetime.datetime.utcnow()))
        print old_file, new_file, path
        folder_path = os.path.join(current_user.get_folder(), path)
        full_path = os.path.join(folder_path, old_file)
        if not os.path.exists(full_path):
            return '{ "result" : -1, "msg" : "file does not exist"}'
        entry = File.query.filter_by(path=path, name=old_file, user=current_user).filter().first()
        entry.name = new_file
        os.rename(full_path, os.path.join(folder_path, new_file))
        db.session.commit()
        return '{ "result" : 1, "msg" : "renamed file"}'
    elif request.json['op'] == 'move':
        file = secure_filename(request.json['file'])
        new_path = sanitize_path(request.json['new_path'])
        old_path = sanitize_path(request.json['old_path'])
        app.logger.info(current_user.username + " moved " + file + " at " + str(datetime.datetime.utcnow()))
        folder_path = os.path.join(current_user.get_folder(), old_path)
        full_path = os.path.join(folder_path, file)
        new_folder_path = os.path.join(current_user.get_folder(), new_path)
        new_full_path = os.path.join(new_folder_path, file)
        if not os.path.exists(full_path):
            return '{ "result" : -1, "msg" : "file does not exist"}'
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        entry = File.query.filter_by(path=sanitize_path(request.json['old_path']), name=file, user=current_user).filter().first()
        entry.path = sanitize_path(request.json['new_path'])
        os.rename(full_path, new_full_path)
        db.session.commit()
        return '{ "result" : 1, "msg" : "moved file"}'
    else:
        return '{ "result" : -1, "msg" : "incorrect or missing parameters"}'

@app.route('/directory/<path:path>', methods=['POST', 'DELETE'])
@login_required
def directory(path):
    if request.method == 'POST':
        path = sanitize_path(path)
        path = os.path.join(current_user.get_folder(), path)
        app.logger.info(current_user.username + " made directory  "+ path + " at " + str(datetime.datetime.utcnow()))
        if not os.path.isdir(path):
            os.makedirs(path)
        #dir = File(current_user.username, '', path, '', datetime.datetime.utcnow())
        return '{ "result" : 1, "msg" : "created path"}'
    else:
        path = sanitize_path(path)
        path = os.path.join(current_user.get_folder(), path)
        app.logger.info(current_user.username + " deleted directory  "+ path + " at " + str(datetime.datetime.utcnow()))
        try:
            os.rmdir(path)
        except:
            return '{ "result" : -1, "msg" : "path not empty"}'
        return '{ "result" : 1, "msg" : "destroyed path"}'

@app.route('/directory', methods=['PUT'])
@login_required
def rename_directory():
    old_path = sanitize_path(request.json['old_path'])
    new_path = sanitize_path(request.json['new_path'])
    app.logger.info(current_user.username + " renamed directory  "+ old_path + " at " + str(datetime.datetime.utcnow()))
    folder_path = os.path.join(current_user.get_folder(), old_path)
    new_folder_path = os.path.join(current_user.get_folder(), new_path)
    print folder_path
    print new_folder_path
    if os.path.exists(new_folder_path):
        return '{ "result" : -1, "msg" : "folder already exists"}'
    if not os.path.exists(folder_path):
        return '{ "result" : -1, "msg" : "folder does not exist"}'
    files = File.query.filter_by(username=current_user.username, path=old_path).all()
    for f in files:
        if f.path.startswith(old_path):
            f.path = f.path.replace(old_path, new_path)
    try:
        os.rename(folder_path, new_folder_path)
        db.session.commit()
        print "rename worked"
        return '{ "result" : 1, "msg" : "folder renamed"}'
    except Exception as e:
        print e
        return '{ "result" : -1, "msg" : "problem renaming folder"}'

@app.route('/session', methods=['DELETE'])
def logout():
    app.logger.info(current_user.username + " logged out at " + str(datetime.datetime.utcnow()))
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
    input = str(data) + str(os.stat(path).st_size) + str(current_user.username)
    return str(hashlib.sha1(str(input)).hexdigest())

def sanitize_path(path):
    if path.startswith('/'):
        return path[1:]
    else:
        return path

if __name__ == '__main__':
    # manager.run()
    # logging.basicConfig(filename='/Users/Will/Desktop/OneDir/OneDir.txt', level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    app.run(threaded=True)