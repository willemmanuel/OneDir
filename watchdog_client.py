__author__ = 'Will'
__author__ = 'cce6g'

from watchdog.events import FileSystemEventHandler
import getpass
import os
from os.path import split,relpath
import errno
import shutil
from oneDirConnection import OneDirConnection
import types
import time
import hashlib
#Custom event handler for Watchdog events
#assumes Linux atm
#Goals: understand event handling in Watchdog and information in the event and possible pitfalls
#issues:
#how to better handle recursive removes that trigger multiple times
#hidden files bork out shutil may need to write custom handler for that
#files can be deleted before being copies i.e. some temp files

class myEventHandler(FileSystemEventHandler):
    """Copies changes in the source folder to the folder copiedTo in the user's home directory"""
    def __init__(self,connection):
        """Defines the destination folder to mimic changes in the source folder and copies the initial contents of the
            source folder over"""
        self.onedir = connection
        super(myEventHandler,self).__init__()
    def on_created(self, event):
        """Handles the creation of new files in the source directory"""
        super(myEventHandler,self).on_created(event)
        #not syncing empty directories serverside atm
        if self.onedir.cookies is None or not self.onedir.autosyncstatus():
            return
        source = event.src_path
        if event.is_directory:
            try:
                pathtoonedir = self.onedir.getonedirrectory()
                relpath =  source.replace(pathtoonedir ,"")
                self.onedir.senddirectory(relpath)
            except Exception as e:
                print "Error syncing directory" + e
                exit(1)
        else:
            source = event.src_path
            try:
                #use os.path.split to get file name and path
                splitpath = split(source)
                file = splitpath[1]
                pathtoonedir = self.onedir.getonedirrectory()
                relpath =  splitpath[0].replace(pathtoonedir ,"")
                self.onedir.sendfile(file, relpath)
            except OSError as e:
                    print "Error copying file! " + e.strerror
                    exit(1)
            except IOError as e:
                    print "IOerror creating file " + e.strerror
                    exit(1)
    def on_moved(self, event):
        """Method to handle moving or renaming of directories and files in the source folder"""
        super(myEventHandler,self).on_moved(event)
        #moveto events from external folders have no src_path
        source = event.src_path
        dest =  event.dest_path
        if event.is_directory:
            splitpath = split(source)
            splitdest = split(dest)
            if splitpath[1] == splitdest[1]:
                    try:
                        #where are we moving from
                        pass
                        #file = splitpath[1]
                        #pathtoonedir = self.onedir.getonedirrectory()
                        #oldpath =  splitpath[0].replace(pathtoonedir ,"")
                        #calculate new path
                        #newpath =  splitdest[0].replace(pathtoonedir ,"")
                        #if oldpath is "":
                        #    oldpath = os.path.sep
                        #self.onedir.movefile(file,newpath,oldpath)
                    except OSError as e:
                        print "Error copying file! " + e
                        exit(1)
            else:
                    #rename!!!!!!!!
                    oldname = source
                    newname = dest
                    pathtoonedir = self.onedir.getonedirrectory()
                    oldname = oldname.replace(pathtoonedir ,"")
                    newname = newname.replace(pathtoonedir ,"")
                    self.onedir.renamedirectory(oldname,newname)
        else:
            #if it comes from outside the folder structure
            if source is None:
                try:
                    #use os.path.split to get file name and path
                    splitpath = split(dest)
                    file = splitpath[1]
                    pathtoonedir = self.onedir.getonedirrectory()
                    relpath =  splitpath[0].replace(pathtoonedir ,"")
                    self.onedir.sendfile(file, relpath)
                except OSError as e:
                    print "Error copying file! " + e.strerror
                    exit(1)
                except IOError as e:
                    print "IOerror creating file " + e.strerror
            else:
                #file was moved!
                #check if name stays the same i.e. it's a move not a rename!
                splitpath = split(source)
                splitdest = split(dest)
                if splitpath[1] == splitdest[1]:
                    try:
                        #where are we moving from
                        file = splitpath[1]
                        pathtoonedir = self.onedir.getonedirrectory()
                        oldpath =  splitpath[0].replace(pathtoonedir ,"")
                        #calculate new path
                        newpath =  splitdest[0].replace(pathtoonedir ,"")
                        if oldpath is "":
                            oldpath = os.path.sep
                        self.onedir.movefile(file,newpath,oldpath)
                    except OSError as e:
                        print "Error copying file! " + e
                        exit(1)
                else:
                    #rename!!!!!!!!
                    file = splitpath[1]
                    newname = splitdest[1]
                    pathtoonedir = self.onedir.getonedirrectory()
                    path =  splitpath[0].replace(pathtoonedir ,"")
                    if path is "":
                        path = os.path.sep
                    else:
                        path = path[1:]
                    self.onedir.rename(file,path,newname)

    def on_deleted(self, event):
        """Method to handle the deleting of files and directories in the source folder"""
        super(myEventHandler,self).on_deleted(event)
        #print "Removed: " + event.src_path
        if self.onedir.cookies is None or not self.onedir.autosyncstatus():
            return

        source = event.src_path
        if event.is_directory:
            try:
                pathtoonedir = self.onedir.getonedirrectory()
                relpath =  source.replace(pathtoonedir ,"")
                self.onedir.deldirectory(relpath)
            except Exception as e:
                print "Error syncing directory" + e
                exit(1)
        else:
            try:
                #use os.path.split to get file name and path
                splitpath = split(source)
                file = splitpath[1]
                pathtoonedir = self.onedir.getonedirrectory()
                #print pathtoonedir
                #print "truncated path:"
                relpath =  splitpath[0].replace(pathtoonedir ,"")
                self.onedir.deletefile(file, relpath)
            except OSError as e:
                    print "Error copying file! " + e.strerror
                    exit(1)
            except IOError as e:
                    print "IOerror creating file " + e.strerror
                    exit(1)

    def on_modified(self, event):
        """Handles modifications to prexisting files and directories in the source folder"""
        super(myEventHandler,self).on_modified(event)
        if event.is_directory:
            try:
                source = event.src_path
                dest = event.src_dest
                pathtoonedir = self.onedir.getonedirrectory()
                source =  source.replace(pathtoonedir ,"")
                dest =  dest.replace(pathtoonedir ,"")
                self.onedir.renamedirectory(source, dest)
            except Exception as e:
                print e
                exit(1)
        else:
            source = event.src_path
            try:
                #use os.path.split to get file name and path
                splitpath = split(source)
                file = splitpath[1]
                if file.startswith('.'):
                    return
                pathtoonedir = self.onedir.getonedirrectory()
                relpath =  splitpath[0].replace(pathtoonedir ,"")
                self.onedir.sendfile(file, relpath)
            except OSError as e:
                    print "Error copying file! " + e.strerror
                    exit(1)
            except IOError as e:
                    print "IOerror creating file " + e.strerror
                    exit(1)