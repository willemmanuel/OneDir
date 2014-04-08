__author__ = 'team33'

import requests
import json
import os
import watchdog
from os.path import expanduser
from oneDirConnection import OneDirConnection
import watchdog
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
def register(oneDir):
        """Handles registration interactions with the user"""
        print "You selected register. Please enter exit to quit or login to try to login:"
        username = raw_input("Please enter your username")
        if(str.lower(username) == 'exit'):
            exit(1)
        password = raw_input("Please enter your password")
        email = raw_input("Please enter your email")
        result = oneDir.register(username,password,email)
        if result == 1:
            print "Thank you for registering, " + username
        else:
            print "Please try again:"

def login(oneDir):
    """Handles individual login interactions"""
    print "You selected login. Please enter exit to quit:"
    username = raw_input("Please enter your username")
    if(str.lower(username) == 'exit'):
            exit(1)
    password = raw_input("Please enter your password")
    result = oneDir.login(username, password)
    if result == 1:
        print "Thank you for logging in!"
        return True
    else:
        print "Issues logging in. Please try again, " + username
        return False

def prompt(oneDir):
    """Prompt to handle initial login/registration"""
    print "Welcome to the OneDir Client"
    success = False
    while True:
        action = raw_input('login, register, or exit?')
        if str.lower(action) == 'register':
            register(oneDir)
        if str.lower(action) == "login":
            success = login(oneDir)
        if str.lower(action) == "exit":
            print "Thank you for trying OneDir"
            exit(1)
        #User is logged in
        if success:
            return

def mainprompt(oneDir, pathtoonedir):
        """Main prompt once user has logged in"""
        userInput = raw_input("Please select an option, " + oneDir.user + " logout, exit, list, get or send")
        if str.lower(userInput) == 'exit':
            oneDir.logout()
            exit(1)
        elif str.lower(userInput) == 'logout':
            oneDir.logout()
            prompt(oneDir)
        elif str.lower(userInput) == 'send':
            filetosend, pathtosend = getfilename('send')
            if oneDir.sendfile(filetosend, pathtosend) == 1:
                print "File sent!"
            else:
                print "Issue sending file"
        elif str.lower(userInput) == 'get':
            filetosend, pathtosend = getfilename('get')
            oneDir.getfile(pathtosend)

        elif str.lower(userInput) == 'list':
            oneDir.list()

        else:
            print "Please enter a valid option!"

def getfilename(typeoffile):
    """Handles promptin for file names"""
    if typeoffile == 'get':
        fileinfo = ""
        pathinfo = raw_input("Which file would you like to get:")
    elif typeoffile == 'send':
        pathinfo = raw_input("Which path in relation to OneDir :")
        fileinfo = raw_input("Which file would you like to send:")
    return fileinfo, pathinfo

def main():
    #host we're connecting to localhost for server on same machine
    host = 'http://127.0.0.1:5000/'
    client = OneDirConnection(host)
    home = expanduser("~")
    oneDir = os.path.join(home,'onedir')
    print oneDir
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, oneDir, recursive=False)
    observer.start()
    prompt(client)
    #we are logdoe# ged in now and the OneDirConnection has an internal cookie
    while True:
        mainprompt(client, oneDir)
if __name__ == '__main__':
    main()

