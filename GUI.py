from Tkinter import *

class App:

    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text="Pull", fg="blue", command=self.pull
            )
        self.button.pack(side=LEFT)

        self.textField = Entry(frame)
        self.textField.pack(side=RIGHT)
        self.v=StringVar()
        self.w=Label(frame, textvariable=self.v)
        self.w.pack()

    def pull(self):
        self.v.set("Searching for your file...")
class PWChange:
    def __init__(self, master):
        frame=Frame(master)
        frame.pack()
        self.userLabel=Label(frame, text="new Username:")
        self.userName=Entry(frame)
        self.userLabel.pack()
        self.userName.pack()
        self.pwLabel=Label(frame, text="new Password:")
        self.pwName=Entry(frame)
        self.pwLabel.pack()
        self.pwName.pack()
        self.button=Button(frame, text="Create User", command=self.check)
        self.button.pack()
        self.varname=StringVar()
        self.w=Label(frame, textvariable=self.varname)
        self.w.pack()
    def check(self):
        f=open('users.txt', 'r')
        item=[self.userName.get(), self.pwName.get()]
        for line in f:
            if line==str(item)+'\n':
                self.varname.set('User Already Exists!')
                f.close()
                return
        f.close()
        with open("users.txt", "a") as f:
            self.varname.set('User Created')
            f.write(str(item)+'\n')
root = Tk()
w=Entry(root)
wl=Label(root, text="username:")
wl.pack()
w.pack()
vl=Label(root, text="password:")
v=Entry(root)
vl.pack()
v.pack()
varname=StringVar()
warn=Label(root, textvariable=varname)
warn.pack()
def access():
    users=[]
    f=open('users.txt', 'r')
    for line in f:
        users.append(line)

    item=[w.get(),v.get()]
    if str(item)+'\n' in users:
        top=Toplevel()
        app = App(top)
    else:
        varname.set('Incorrect Username/Password')

def new():
    top=Toplevel()
    app=PWChange(top)
b=Button(root, text="->", command= access)
newUserButton=Button(root, text="Create New User", command=new)
b.pack()
newUserButton.pack()
root.mainloop()
root.destroy() # optional; see description below
