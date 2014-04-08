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
#Custom event handler for Watchdog events
#assumes Linux atm
#Goals: understand event handling in Watchdog and information in the event and possible pitfalls
#issues:
#how to better handle recursive removes that trigger multiple times
#hidden files bork out shutil may need to write custom handler for that
#files can be deleted before being copies i.e. some temp files

USER = 'OneDir'
PASS = 'test'


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
        """
        if event.is_directory:
            try:
                os.makedirs(copyTo)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        else: """

        source = event.src_path
        try:
            #use os.path.split to get file name and path
            splitpath = split(source)
            file = splitpath[1]
            pathtoonedir = self.onedir.getonedirrectory()
            print pathtoonedir
            print splitpath[0]
            print "truncated path:"
            print splitpath[0].replace(pathtoonedir ,"")
            relapath = ""
            relpath =""
            self.onedir.sendfile(file,relpath)
        except OSError as e:
                    print "Error copying file! " + e.strerror
                    exit(1)
        except IOError as e:
                    print "IOerror creating file " + e.strerror
                    exit(1)
    """
    def on_moved(self, event):
        Method to handle moving or renaming of directories and files in the source folder
        super(myEventHandler,self).on_moved(event)
        #moveto events from external folders have no src_path
        print "moving to:" + event.dest_path
        if event.is_directory:
            source = event.src_path.replace('/testfolder/testdir','/testfolder/copiedTo')
            destination = event.dest_path.replace('/testfolder/testdir','/testfolder/copiedTo')
            os.rename(source,destination)
        else:
            #if it comes from outside the folder structure
            source = event.dest_path
            destination = event.dest_path.replace('/testfolder/testdir','/testfolder/copiedTo')
            try:
                if event.src_path is not None:
                    os.remove(event.src_path.replace('/testfolder/testdir','/testfolder/copiedTo'))
                shutil.copyfile(source,destination)
            except OSError as e:
                print "Error copying file! " + e
                exit(1)
    """
    """
    def on_deleted(self, event):
        Method to handle the deleting of files and directories in the source folder
        super(myEventHandler,self).on_deleted(event)
        print "Removed: " + event.src_path
        if event.is_directory:
            source = event.src_path.replace('/testfolder/testdir','/testfolder/copiedTo')
            try:
                os.rmdir(source)
            except OSError as e:
                if e.errno != 2:
                    print e
                    exit(1)
        else:
            source = event.src_path.replace('/testfolder/testdir','/testfolder/copiedTo')
            try:
                os.remove(source)
            except OSError as e:
                print "Error deleting file! " + e
                exit(1)
    def on_modified(self, event):
        Handles modifications to prexisting files and directories in the source folder
        super(myEventHandler,self).on_modified(event)
        print "Modified: " + event.src_path
        if event.is_directory:
            pass
        else:
            destination = event.src_path.replace('/testfolder/testdir','/testfolder/copiedTo')
            try:
                shutil.copyfile(event.src_path,destination)
            except OSError as e:
                print "Error copying file! " + e
                exit(1)
    """