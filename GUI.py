import tkMessageBox as messagebox
import Tkinter as tk
import os
from os.path import expanduser
from oneDirConnection import OneDirConnection
from watchdog.observers import Observer
from watchdog_client import myEventHandler

class Login:
    def __init__(self, master, oneDir):
        self.oneDir = oneDir
        self.master = master
        self.frame = tk.Frame(self.master, padx=10, pady=10)
        tk.Label(self.frame, text="Welcome to OneDir", height=2).pack(side=tk.TOP)
        tk.Label(self.frame, text="Username").pack(side=tk.TOP)
        self.user = tk.Entry(self.frame)
        self.user.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
        tk.Label(self.frame, text="Password").pack(side=tk.TOP)
        self.password = tk.Entry(self.frame, show="*")
        self.password.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
        self.error = tk.Label(self.frame, text="Incorrect combination", fg="red")
        b = tk.Button(self.frame, borderwidth=4, text="Login", width=10, pady=8, command=self.check_password)
        b.pack(side=tk.BOTTOM)
        self.password.bind('<Return>', self.enter)
        self.frame.pack(fill=tk.BOTH, expand=True)

    def enter(self, event):
        self.check_password()

    def check_password(self):
        try:
            if self.oneDir.login(self.user.get(), self.password.get()) == 1:
                Settings(self.master, self.oneDir)
                self.frame.destroy()
            else:
                self.error['text'] = "Incorrect combination"
                self.error.pack(side=tk.TOP)
        except:
            self.error['text'] = "Cannot connect to server"
            self.error.pack(side=tk.TOP)

class Settings:
    def __init__(self, master, oneDir):
        self.oneDir = oneDir
        self.master = master
        self.frame = tk.Frame(self.master)
        t = "Welcome, " + self.oneDir.user + "!"
        tk.Label(self.frame, text=t).pack(side=tk.TOP)
        self.toggle_autosync_button = tk.Button(self.frame, text = 'Disable autosync', width = 25, command = self.toggle_autosync)
        self.toggle_autosync_button.pack()
        self.change_password_button = tk.Button(self.frame, text = 'Change password', width = 25, command = self.change_password)
        self.change_password_button.pack()
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        messagebox.showinfo(message='Logged in successfully! Syncing now')
        self.oneDir.enableautosync()
        self.oneDir.full_sync()
        self.frame.pack()

    def toggle_autosync(self):
        if self.oneDir.autosyncstatus():
            messagebox.showinfo(message='Turning autosync off')
            self.toggle_autosync_button['text'] = 'Enable autosync'
            self.oneDir.disableautosync()
        else:
            messagebox.showinfo(message='Turning autosync on')
            self.toggle_autosync_button['text'] = 'Disable autosync'
            self.oneDir.enableautosync()

    def change_password(self):
        print "button clicked"

    def close_windows(self):
        ans = messagebox.askyesno(message='Are you sure you want to quit?', icon='question', title='Logout')
        if ans:
            self.master.destroy()

def main():
    host = 'http://127.0.0.1:5000/'
    # home = expanduser("~")
    # oneDir = os.path.join(home,'onedir')
    dir = '/Users/Will/Desktop/client'
    client = OneDirConnection('http://127.0.0.1:5000/', '/Users/Will/Desktop/client')
    event_handler = myEventHandler(client)
    observer = Observer()
    observer.schedule(event_handler, dir, recursive=True)
    observer.start()
    root = tk.Tk()
    root.geometry('200x250')
    root.title('OneDir')
    app = Login(root, client)
    root.mainloop()


if __name__ == '__main__':
    main()