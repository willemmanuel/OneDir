import requests
import json
import os
from os.path import join,expanduser

class OneDirConnection:
    """Class to facilitate managing network communication between the oneDir client and server."""

    def __init__(self, host):
        """Constructor which setsup the host the server is at"""
        self.host = host
        self.cookies = None
        self.user = None
        home = expanduser("~")
        self.onedirrectory = '/Users/Will/Desktop/client/'

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
        print path
        url = self.host + 'file/' + path
        results = requests.post(url,  files={'file': open(file, 'rb')}, cookies=self.cookies)
        print results.text
        if results.json()['result'] == -1:
            return -1
        else:
            return 1

    def getfile(self, file):
        """Gets a file from the OneDir server using the internal cookie stored inside"""
        path = os.path.join(file['path'], file['name'])
        url = self.host + 'file/' + path
        results = requests.get(url, cookies=self.cookies)
        return results.text

    def list(self):
        url = self.host + 'list'
        results = requests.get(url, cookies=self.cookies)
        return json.loads(results.text)['files']

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