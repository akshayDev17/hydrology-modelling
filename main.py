import os
import assignment1
from tkinter import Tk, Menu, Button, Message, Toplevel, filedialog, messagebox
top = Tk()
top.geometry("500x500")
top.title("Course Project")
menubar = Menu(top)

file = Menu(menubar, tearoff=0)
file.add_command(label="New")
file.add_command(label="Open")
file.add_command(label="Save")
file.add_command(label="Save As...")
file.add_command(label="Close")
file.add_separator()
file.add_command(label="Exit", command=top.quit)

menubar.add_cascade(label="File", menu=file)

edit = Menu(menubar, tearoff=0)  
edit.add_command(label="Undo")  
  
edit.add_separator()  
  
edit.add_command(label="Cut")  
edit.add_command(label="Copy")  
edit.add_command(label="Paste") 
edit.add_command(label="Delete")  
edit.add_command(label="Select All")  
menubar.add_cascade(label="Edit", menu=edit)

def about():
    about_window = Toplevel(top)
    about_window.geometry("600x200")
    msg = Message(about_window, width=500,  text="1. This program can generate a mask file by reading only the shape file of a basin.\n\n\
2. It can also perform watershed delineation by reading a DEM geotiff file and mask file of a river basin")
    msg.pack()
    about_window.mainloop()

def findExtension(name):
    ans = ""
    sz = len(name)
    i = sz - 1
    while i >= 0:
        if name[i] == '.':
            ans = ans[::-1]
            return ans
        else:
            ans+=name[i]
        i -= 1

def get_file():
    cwd = os.getcwd()
    fileObj = filedialog.askopenfile(initialdir=cwd,
                           filetypes =(("Shape File", "*.shp"),("All Files","*.*")),
                           title = "Choose a file.")
    filename = fileObj.name
    extension = findExtension(filename)
    if extension == 'shp':
        assignment1.giveMask(filename)
    else:
        messagebox.showerror("error", "The file selected was not a .shp file.")


    

def shapeToMask():
    new_window = Toplevel(top)
    new_window.geometry("150x150")
    txt = Message(new_window, width=150, text="Choose a shape file")
    txt.pack()
    browse_button = Button(new_window, text="Browse..", command=get_file)
    browse_button.place(x = 40, y = 50)
    new_window.mainloop()

  
options = Menu(menubar, tearoff=0)
options.add_command(label="Generate Mask file...", command=shapeToMask)
menubar.add_cascade(label="Options", menu=options)

help = Menu(menubar, tearoff=0)  
help.add_command(label="About", command=about)  
menubar.add_cascade(label="Help", menu=help)  


top.config(menu=menubar)  
top.mainloop()  