from oneDirConnection import OneDirConnection
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

# from http://effbot.org/tkinterbook/entry.htm
oneDir = OneDirConnection('http://127.0.0.1:5000/', '/Users/Will/Desktop/client')
def make_entry(parent, caption, width=None, **options):
    tk.Label(parent, text=caption).pack(side=tk.TOP)
    entry = tk.Entry(parent, **options)
    if width:
        entry.config(width=width)
    entry.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
    return entry

def enter(event):
    check_password()

def check_password():
    """ Collect 1's for every failure and quit program in case of failure_max failures """
    if oneDir.login(user.get(), password.get()) == 1:
        root.destroy()
        print('Logged in')
        return
    else:
        error.pack(side=tk.TOP)

root = tk.Tk()
root.geometry('200x250')
root.title('OneDir')
#frame for window margin
parent = tk.Frame(root, padx=10, pady=10)
parent.pack(fill=tk.BOTH, expand=True)
#entrys with not shown text
tk.Label(parent, text="Welcome to OneDir", height=2).pack(side=tk.TOP)
user = make_entry(parent, "User name:", 16)
password = make_entry(parent, "Password:", 16, show="*")
error = tk.Label(parent, text="Incorrect combination", fg="red")
#button to attempt to login
b = tk.Button(parent, borderwidth=4, text="Login", width=10, pady=8, command=check_password)
b.pack(side=tk.BOTTOM)
password.bind('<Return>', enter)
user.focus_set()
parent.mainloop()

# Need to use views!
# import Tkinter as tk
#
# class View(tk.Frame):
#     count = 0
#     def __init__(self, *args, **kwargs):
#         tk.Frame.__init__(self, *args, **kwargs)
#         b = tk.Button(self, text="Open new window", command=self.new_window)
#         b.pack(side="top")
#
#     def new_window(self):
#         self.count += 1
#         id = "New window #%s" % self.count
#         window = tk.Toplevel(self)
#         label = tk.Label(window, text=id)
#         label.pack(side="top", fill="both", padx=10, pady=10)
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     view = View(root)
#     view.pack(side="top", fill="both", expand=True)
#     root.mainloop()
