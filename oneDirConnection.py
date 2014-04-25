import requests
import json
import os
from os.path import join, expanduser
from Queue import Queue
import re
import hashlib
import time
import httplib
class OneDirConnection:
    """Class to facilitate managing network communication between the oneDir client and server."""
    def __init__(self, host, direct):
        """Constructor which setsup the host the server is at"""
        self.host = host
        self.cookies = None
        self.user = None
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
    def changepassword(self, password):
        url = self.host + 'change_password'
        headers = {'Content-Type': 'application/json'}
        data = {'password': password}
        results = requests.put(url, headers=headers, data=json.dumps(data), cookies=self.cookies)
        self.logout()
    def admin_changepassword(self, user, password):
        url = self.host + 'admin/change_password'
        headers = {'Content-Type': 'application/json'}
        data = {'user' : user, 'password': password}
        results = requests.put(url, headers=headers, data=json.dumps(data), cookies=self.cookies)
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
        if results.status_code == 500:
            print "Databse error!,exiting"
            exit(1)
        if results is None:
            print "Database rror talking to server!"
            exit(1)
        if results.json()['result'] == -1:
            return -1
        else:
            return 1
    def deletefile(self,file,path):
        """Send a request to the server to delete a file the user has removed"""
        url = self.host + 'file'
        path = self.sanitize_path(path)
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
        path = self.sanitize_path(file['path'])
        if path:
            path = os.path.join(path, file['name'])
        else:
            path = os.path.join(file['name'])
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
        result = requests.put(url, headers=headers, data=json.dumps(data), cookies=self.cookies)
    def list(self):
        url = self.host + 'list'
        results = requests.get(url, cookies=self.cookies)
        try:
            return json.loads(results.text)['files']
        except:
            return None
    def admin_list(self):
        url = self.host + 'admin/list'
        results = requests.get(url, cookies=self.cookies)
        try:
            return json.loads(results.text)['files']
        except:
            return None
    def admin_delete(self, user, file, path):
        url = self.host + 'admin/file'
        headers = {'Content-Type': 'application/json'}
        data = {'user': user, 'path': path, 'file': file}
        result = requests.delete(url, cookies=self.cookies, headers=headers, data=json.dumps(data))
        print result.text
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
        print self.filelist
        if self.filelist:
            for f in self.filelist:
                path = self.sanitize_path(f['path'])
                path = os.path.join(self.onedirrectory, path)
                print path
                print self.exists(f)
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
            if os.listdir(directory[0]) == []:
                e = directory[0].replace(self.onedirrectory, "")
                self.senddirectory(e)
                print e
            for f in directory[2]:
                if f.startswith('.'):
                    continue
                path = os.path.join(directory[0], f)
                if path not in self.synced:
                    d = directory[0].replace(self.onedirrectory, "")
                    self.sendfile(f, d)
                    self.synced.append(path)
    def hash_file(self, file):
        print file
        path = self.sanitize_path(file['path'])
        # if not root directory
        if path:
            path = os.path.join(self.onedirrectory, path)
            path = os.path.join(path, file['name'])
        else:
            path = os.path.join(self.onedirrectory, file['name'])

        print path
        with open(path, 'rb') as f:
            data = f.read()
        input = str(data) + str(os.stat(path).st_size) + str(self.user)
        return hashlib.sha1(str(input)).hexdigest()

    def make_path(self, file):
        path = self.sanitize_path(file['path'])
        if path:
            path = os.path.join(self.onedirrectory, path)
            path = os.path.join(path, file['name'])
            return str(path)
        else:
            return str(os.path.join(self.onedirrectory, file['name']))

    def senddirectory(self,path):
        if path[0] == '/':
            path = path[1:]
        url = self.host + 'directory/' + path
        results = requests.post(url, cookies=self.cookies)
        return results.text
    def deldirectory(self,path):
        if path[0] == '/':
            path = path[1:]
        url = self.host + 'directory/' + path
        results = requests.delete(url, cookies=self.cookies)
        return results.text
    def renamedirectory(self, old_path, new_path):
        url = self.host + 'directory'
        headers = {'Content-Type': 'application/json'}
        data = {'old_path' : old_path, 'new_path' : new_path}
        result = requests.put(url, headers=headers, data=json.dumps(data), cookies=self.cookies)
        print result
        return 1
        #return result.json['result']

    def exists(self, file):
        return os.path.isfile(self.make_path(file))

    def sanitize_path(self, path):
        if path.startswith('/'):
            return str(path[1:])
        else:
            return str(path)