import requests
import json
from os.path import join,expanduser
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
        if self.connection.login(user, password) != user:
            raise Exception
        self.list = None
        self.full_sync()

#
    #
    # sin(theta) = 1.22 * wavelength / diameter
    # wavelentgh = wavelength light / vitrus humor
    #
    #
    #

    # for file in onedir:
    #   if f not in list():
    #    post
    #   if f in list but metadata missing:
    #    out of date post, moved post, etc
    #   if in list but not onedir
    #    pull

    def full_sync(self):
        self.list = json.dumps(self.connection.list())
        # for f in self.list:



    def hash_file(self, path):
        with open(path, 'rb') as f:
            data = f.read()
        return hashlib.sha1(data + str(os.stat(path).st_size) + str(self.user)).hexdigest()