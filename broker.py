import requests
import json
from os.path import join,expanduser
import os
import oneDirConnection
import hashlib
import os
import time
import json

class Broker:
    def __init__(self, onedir):
        """Constructor which sets up the host the server is at"""
        home = expanduser("~")
        self.onedirrectory = home + '/onedir'
        self.connection = onedir
        self.host = self.connection.host
        self.user = self.connection.user
        if self.connection.cookies is None:
            raise Exception
        self.list = None
        self.full_sync()

    def full_sync(self):
        self.list = self.connection.list()
        self.synced = []
        if self.list:
            for f in self.list:
                if f['path'] == '/':
                    path = self.onedirrectory
                else:
                    path = os.path.join(self.onedirrectory, f['path'])
                if not os.path.exists(path):
                    os.makedirs(path)
                if not self.exists(f):
                    data = self.connection.getfile(f)
                    with open(self.make_path(f), 'a') as new_file:
                        new_file.write(data)
                        new_file.close()
                elif str(self.hash_file(f)) != str(f['hash']):
                    self.connection.sendfile(f['name'], f['path'])
                if self.make_path(f) not in self.synced:
                    self.synced.append(self.make_path(f))
        os_walk = os.walk(self.onedirrectory)
        for directory in os_walk:
            for f in directory[2]:
                if f.startswith('.'):
                    continue
                path = os.path.join(directory[0], f)
                if path not in self.synced:
                    d = directory[0].replace(self.onedirrectory, "")
                    self.connection.sendfile(f, d)
                    self.synced.append(path)

    def hash_file(self, file):
        if file['path'] == '/':
            path = os.path.join(self.onedirrectory, file['name'])
        else:
            path = os.path.join(self.onedirrectory, file['path'], file['name'])
        with open(path, 'rb') as f:
            data = f.read()
        input = str(data) + str(os.stat(path).st_size) + str(self.user)
        return hashlib.sha1(str(input)).hexdigest()

    def make_path(self, file):
        if file['path'] == '/':
            return str(os.path.join(self.onedirrectory, file['name']))
        return str(os.path.join(self.onedirrectory, file['path'], file['name']))

    def exists(self, file):
        return os.path.isfile(self.make_path(file))

def main():
    # For demoing
    # server = raw_input("Server address: ")
    # user = raw_input("Username: ")
    # password = raw_input("Password: ")
    # onedir = raw_input("OneDir: ")
    # x = Broker(server, user, password, onedir)

    x = Broker("http://127.0.0.1:5000/", "OneDir", 'test', '/Users/Will/Desktop/client')
    while True:
        time.sleep(10)
        x.full_sync()

#main()