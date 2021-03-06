__author__ = 'christopher'
import os
import time
import threading
from oneDirConnection import OneDirConnection
class syncthread(threading.Thread):
    def __init__(self,loggedinuser):
        threading.Thread.__init__(self)
        self.loggedin = loggedinuser
        self.onedirrectory = self.loggedin.getonedirrectory()
        self.shutdown  = False
    def run(self):
        print "Starting sync thread"
        self.half_sync(10)
        print "Stopping sync thread"
    def half_sync(self,delay):
            """don't resync files deleted from server"""
            self.count = 1
            while not self.shutdown and self.loggedin.autosync:
                time.sleep(delay)
                self.count += 1
                self.filelist = self.loggedin.list()
                print "Pinged server for changes"
                self.synced = []
                if self.filelist:
                    for f in self.filelist:
                        path = self.loggedin.sanitize_path(f['path'])
                        path = os.path.join(self.onedirrectory, path)
                        if not os.path.exists(path):
                            os.makedirs(path)
                        if f['name'] and not self.loggedin.exists(f):
                            exists, data = self.loggedin.getfile(f)
                            if exists:
                                with open(self.loggedin.make_path(f), 'a') as new_file:
                                    new_file.write(data)
                                    new_file.close()
                        elif f['name'] and str(self.loggedin.hash_file(f)) != str(f['hash']):
                            self.loggedin.sendfile(f['name'], f['path'])
                        if self.loggedin.make_path(f) not in self.synced:
                            self.synced.append(self.loggedin.make_path(f))
                os_walk = os.walk(self.loggedin.onedirrectory)
                for directory in os_walk:
                    for f in directory[2]:
                        if f.startswith('.'):
                            continue
                        path = os.path.join(directory[0], f)
                        if path not in self.synced:
                            try:
                                os.remove(path)
                            except OSError, e:
                                print ("Error: %s - %s." % (e.filename,e.strerror))

