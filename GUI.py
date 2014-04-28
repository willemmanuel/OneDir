import tkMessageBox as messagebox
import Tkinter as tk
from ago import human
import os
from os.path import expanduser
import tkFileDialog as fdialog
from oneDirConnection import OneDirConnection
from watchdog.observers import Observer
from watchdog_client import myEventHandler
import datetime

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
        c = tk.Button(self.frame, borderwidth=4, text="Sign Up", width=10, pady=8, command=self.new_user)
        c.pack(side=tk.BOTTOM)
        self.password.bind('<Return>', self.enter)
        self.frame.pack(fill=tk.BOTH, expand=True)

    def enter(self, event):
        self.check_password()
        newUserWindow=tk.Frame
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
    def new_user(self):
        NewUser(self.master, self.oneDir)

class Settings:
    def __init__(self, master, oneDir):
        messagebox.showinfo(message='Logged in successfully! Syncing now')
        self.oneDir = oneDir
        self.master = master
        self.frame = tk.Frame(self.master)
        t = "Welcome, " + self.oneDir.user + "!"
        self.master.geometry('200x200')
        tk.Label(self.frame, text=t).pack(side=tk.TOP)
        self.toggle_autosync_button = tk.Button(self.frame, text = 'Disable autosync', width = 25, command = self.toggle_autosync)
        self.toggle_autosync_button.pack()
        self.change_password_button = tk.Button(self.frame, text = 'Change password', width = 25, command = self.change_password)
        self.change_password_button.pack()
        self.change_directory_button = tk.Button(self.frame, text = 'Change OneDir path', width = 25, command = self.change_directory)
        self.change_directory_button.pack()
        self.list_files = tk.Button(self.frame, text = 'List server files', width = 25, command = self.list)
        self.list_files.pack()
        self.update = tk.Button(self.frame, text = 'Force sync', width = 25, command = self.sync)
        self.update.pack()
        self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.oneDir.enableautosync()
        self.oneDir.full_sync()
        self.frame.pack()
    def list(self):
        List(self.master, self.oneDir)

    def sync(self):
        self.oneDir.full_sync()

    def change_directory(self):
        path = fdialog.askdirectory()
        if path:
            self.oneDir.onedirrectory = path
            self.oneDir.full_sync()
            return True
        return False

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
        ChangePassword(self.master, self.oneDir)

    def close_windows(self):
        ans = messagebox.askyesno(message='Are you sure you want to quit?', icon='question', title='Logout')
        if ans:
            self.master.destroy()
class NewUser:
     def __init__(self, master, oneDir):
        self.master = master
        self.oneDir = oneDir
        self.frame = tk.Toplevel(self.master,padx=10, pady=10)
        tk.Label(self.frame, text="Welcome, New User", height=2).pack(side=tk.TOP)
        tk.Label(self.frame, text="New Username").pack(side=tk.TOP)
        self.user = tk.Entry(self.frame)
        self.user.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
        tk.Label(self.frame, text="New Password").pack(side=tk.TOP)
        self.password = tk.Entry(self.frame, show="*")
        self.password.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
        tk.Label(self.frame, text="Your Email").pack(side=tk.TOP)
        self.email = tk.Entry(self.frame)
        self.email.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
        self.error = tk.Label(self.frame, text="User/password not unique", fg="red")
        c = tk.Button(self.frame, borderwidth=4, text="Sign Up", width=10, pady=8, command=self.new_user)
        c.pack(side=tk.BOTTOM)
     def new_user(self):
        try:
            if self.oneDir.register(self.user.get(), self.password.get(), self.email.get()) == -1:
                    self.error['text'] = "User/password not unique"
                    self.error.pack(side=tk.TOP)
            else:
                self.frame.destroy()
        except:
            self.error['text'] = "Cannot connect to server"
            self.error.pack(side=tk.TOP)

class ChangePassword:
     def __init__(self, master, oneDir):
        self.master = master
        self.oneDir = oneDir
        self.frame = tk.Toplevel(self.master)
        if self.oneDir.user == 'admin':
            tk.Label(self.frame, text="User").pack(side=tk.TOP)
            self.user = tk.Entry(self.frame)
            self.user.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
        tk.Label(self.frame, text="New Password").pack(side=tk.TOP)
        self.password = tk.Entry(self.frame, show="*")
        self.password.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
        c = tk.Button(self.frame, borderwidth=4, text="Submit", width=10, pady=8, command=self.change_password)
        c.pack(side=tk.BOTTOM)
     def change_password(self):
        if self.oneDir.user == 'admin':
            try:
                self.oneDir.admin_changepassword(self.user.get(), self.password.get())
                messagebox.showinfo(message='Password changed')
            except:
                messagebox.showinfo(message='Error changing password')
        try:
            self.oneDir.changepassword(self.password.get())
            messagebox.showinfo(message='Password changed')
        except:
            messagebox.showinfo(message='Error changing password')

        self.frame.destroy()

class List:
    def __init__(self, master, oneDir):
        self.oneDir = oneDir
        self.master = master
        self.frame = tk.Toplevel(self.master)
        if self.oneDir.user == 'admin':
            self.list = self.oneDir.admin_list()
        else:
            self.list = self.oneDir.list()
        print self.list
        self.entries = {}
        counter = 1
        tk.Label(self.frame, text="User").grid(row = 1, column=1)
        tk.Label(self.frame, text="File").grid(row = 1, column=2)
        tk.Label(self.frame, text="Path").grid(row = 1, column=3)
        tk.Label(self.frame, text="Modified").grid(row = 1, column=4)
        tk.Label(self.frame, text="Delete").grid(row = 1, column=5)
        tk.Label(self.frame, text="Share").grid(row = 1, column=6)
        count = 2
        for f in self.list:
            tk.Label(self.frame, text=f['username']).grid(row = count, column=1)
            tk.Label(self.frame, text=f['name']).grid(row = count, column=2)
            tk.Label(self.frame, text='/' + f['path']).grid(row = count, column=3)
            modified = human(datetime.datetime.strptime(f['modified'], '%Y-%m-%d %H:%M:%S.%f'), precision=2, past_tense='{} ago', future_tense='in {}')
            tk.Label(self.frame, text=modified).grid(row = count, column=4)
            tk.Button(self.frame, borderwidth=4, text="Delete", width=10, pady=8, command=lambda count=count: self.delete(count)).grid(row=count, column=5)
            tk.Button(self.frame, borderwidth=4, text="Share", width=10, pady=8, command=lambda count=count: self.share(count)).grid(row=count, column=6)
            count += 1

    def delete(self, count):
        count -= 2
        f = self.list[count]
        if self.oneDir.user == 'admin':
            self.oneDir.admin_delete(f['username'], f['name'], f['path'])
        else:
            self.oneDir.deletefile(f['name'], f['path'])
            full_path = os.path.join(self.oneDir.getonedirrectory(), self.oneDir.sanitize_path(f['path']))
            full_path = os.path.join(full_path, f['name'])
            os.remove(full_path)
        List(self.master, self.oneDir)
        self.frame.destroy()

    def share(self, count):
        count -= 2
        f = self.list[count]
        ShareFile(self.master, self.oneDir, f)

class ShareFile:
     def __init__(self, master, oneDir, file):
        self.master = master
        self.oneDir = oneDir
        self.file = file
        self.frame = tk.Toplevel(self.master)
        tk.Label(self.frame, text="User to share with").pack(side=tk.TOP)
        self.user = tk.Entry(self.frame)
        self.user.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
        c = tk.Button(self.frame, borderwidth=4, text="Submit", width=10, pady=8, command=self.share_file)
        c.pack(side=tk.BOTTOM)
     def share_file(self):
        try:
            self.oneDir.postsharedfile(self.user.get(), self.file['name'], self.file['path'])
            messagebox.showinfo(message='File shared')
            self.frame.destroy()
        except:
            messagebox.showinfo(message='Error sharing file')

def main():
    host = 'http://127.0.0.1:5000/'
    #home = expanduser("~")
    #oneDir = os.path.join(home,'onedir')
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