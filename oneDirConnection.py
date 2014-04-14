import requests
import json
import os
from os.path import join, expanduser
from Queue import Queue
import re
import hashlib
import time
class OneDirConnection:
    """Class to facilitate managing network communication between the oneDir client and server."""

    def __init__(self, host, direct):
        """Constructor which setsup the host the server is at"""
        self.host = host
        self.cookies = None
        self.user = None
        home = expanduser("~")
        self.onedirrectory = direct
        self.autosync = False
    def getonedirrectory(self):
        """ask for the current onedir directory location for the user using this connection"""
        return self.onedirrectory
    def register(self, username ,password, email):
        """Register the given username , password and email with the oneDir server"""
        #build the request to send.
        url = self.host + "register"
        data = {'username': username, 'password': password, 'email': email}
        headers = {'Content-Type': 'application/json'}
        results = requests.post(url, data=json.dumps(data), headers=headers)
        # If it returns username it worked otherwise we have an issue. Update with more pertinent data once server works for me
        if results.json()['result'] == username:
            return 1
        else:
            return -1

    def login(self, username, password):
        """Login to the oneDir server saving the cookie internally to preserve session"""
        url = self.host + "session"
        data = {'username': username, 'password': password}
        headers = {'Content-Type': 'application/json'}
        results = requests.post(url, data=json.dumps(data), headers=headers)
        self.cookies = results.cookies
        if results.json()['result'] == username:
            self.user = username
            return 1
        else:
            return -1

    def sendfile(self, file, path):
        """Sends a file to the OneDir server using the internal cookie stored inside"""
        if path == "" or path == "/":
            url = self.host + 'file'
            file = os.path.join(self.onedirrectory, file)
        else:
            if path[0] == os.sep:
                path = path[1:]
            url = self.host + 'file/' + path
            file = os.path.join(self.onedirrectory, path, file)
        results = requests.post(url,  files={'file': open(file, 'rb')}, cookies=self.cookies)
        if results.json()['result'] == -1:
            return -1
        else:
            return 1
    def deletefile(self,file,path):
        """Send a request to the server to delete a file the user has remove"""
        if path == "" or path == "/":
            url = self.host + 'file'
        else:
            if path[0] == os.sep:
                path = path[1:]
            url = self.host + 'file/' + path
        headers = {'Content-Type': 'application/json'}
        data = {'file' : file, 'path' : path}
        print "file:" + file + " path: " + path
        results = requests.delete(url, headers=headers, data=json.dumps(data), cookies=self.cookies)
        if results.json()['result'] == -1:
            return -1
        else:
            return 1
    def getfile(self, file):
        """Gets a file from the OneDir server using the internal cookie stored inside"""
        if file['path'] == '' or file['path'] == '/':
            path = os.path.join(file['name'])
        else:
            path = os.path.join(file['path'], file['name'])
        url = self.host + 'file/' + path
        results = requests.get(url, cookies=self.cookies)
        return results.text
    def movefile(self,file,newpath,oldpath):
        """move a file already in the directory to another location on the server"""
        url = self.host + 'file'
        headers = {'Content-Type': 'application/json'}
        data = {'op':'move', 'file' : file, 'old_path' : oldpath, 'new_path' : newpath}
        results = requests.put(url, headers=headers, data=json.dumps(data), cookies=self.cookies)
        if results.json()['result'] == -1:
            #failureee
            return -1
        else:
            #greatsuccess
            return 1
    def rename(self,oldname,path,newname):
        """Rename the given file on the server"""
        url = self.host + 'file'
        headers = {'Content-Type': 'application/json'}
        data = {'op':'rename', 'old_file' : oldname, 'path' : path, 'new_file' : newname}
        #print "oldname: " + oldname
        #print "path: " + path
        #print "newname:" + newname
        result = requests.put(url, headers=headers, data=json.dumps(data), cookies=self.cookies)
    def list(self):
        url = self.host + 'list'
        results = requests.get(url, cookies=self.cookies)
        try:
            return json.loads(results.text)['files']
        except:
            return None

    def logout(self):
        """Logout from the oneDir api server"""
        url = self.host + "session"
        headers = {'Content-Type': 'application/json'}
        result = requests.delete(url, cookies=self.cookies, headers=headers)
        self.cookies = None
        if result.json()['result'] == self.user:
            return 1
        else:
            return -1
    def autosyncstatus(self):
        """Returns the value of the autosync member"""
        return self.autosync
    def enableautosync(self):
        """Toggle autosync on"""
        self.autosync = True
    def disableautosync(self):
        """Set autosync to false"""
        self.autosync = False
    def getuser(self):
        """Getter for logged in user"""
        return self.user
    def loggedin(self):
        """Check whether user is logged in currently"""
        return self.cookies is not None
    def full_sync(self):
        """sync thefiles between the server and client"""
        self.filelist = self.list()
        self.synced = []
        if self.filelist:
            for f in self.filelist:
                if f['path'] == '/':
                    path = self.onedirrectory
                else:
                    path = os.path.join(self.onedirrectory, f['path'])
                if not os.path.exists(path):
                    os.makedirs(path)
                if not self.exists(f):
                    data = self.getfile(f)
                    with open(self.make_path(f), 'a') as new_file:
                        new_file.write(data)
                        new_file.close()
                elif str(self.hash_file(f)) != str(f['hash']):
                    self.sendfile(f['name'], f['path'])
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
                    self.sendfile(f, d)
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