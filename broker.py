import requests
import json
from os.path import join,expanduser
import os
from Queue import Queue
import oneDirConnection
import hashlib
import os
import json

class Broker:
    def __init__(self, host, user, password):
        """Constructor which sets up the host the server is at"""
        self.user = user
        home = expanduser("~")
        self.q = Queue()
        self.onedirrectory = '/Users/Will/Desktop/client/'
        self.host = host
        self.connection = oneDirConnection.OneDirConnection(host)
        if self.connection.login(user, password) != 1:
            raise Exception
        self.list = None
        self.full_sync()

    def full_sync(self):
        self.list = self.connection.list()
        self.synced = []
        for f in self.list:
            path = os.path.join(self.onedirrectory, f['path'])
            if not os.path.exists(path):
                os.makedirs(path)
            if not self.exists(f):
                data = self.connection.getfile(f)
                new_file = open(self.make_path(f), 'a')
                new_file.write(data)
            elif self.hash_file(f) != f['hash']:
                self.connection.sendfile(f)
            self.synced.append(self.make_path(f))
        for root, dirs, files in os.walk(self.onedirrectory):
            print root, dirs, files

    def hash_file(self, file):
        path = os.path.join(self.onedirrectory, file['path'], file['name'])
        with open(path, 'rb') as f:
            data = f.read()
        return hashlib.sha1(data + str(os.stat(path).st_size) + str(self.user)).hexdigest()

    def make_path(self, file):
        return str(os.path.join(self.onedirrectory, file['path'], file['name']))

    def exists(self, file):
        return os.path.isfile(self.make_path(file))

def main():
    x = Broker("http://127.0.0.1:5000/", "OneDir", "test")

main()