import os
import assignment1
import assignment_3
from tkinter import Tk, Menu, Button, Message, Toplevel, filedialog, messagebox, Label, LEFT, X, RIGHT, Entry, StringVar, YES, W, E


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
    about_window.resizable(True, True)
    asgn1 = Label(about_window, text="1. This program can generate a mask file by reading only the shape file of a basin.")
    asgn1.grid(row=0, sticky=W)

    asgn2_1 = Label(about_window, text="2. It can perform watershed delineation, with a DEM.tif DEM data file as the input.")
    asgn2_1.grid(row=1, sticky=W)

    asgn2_2 = Label(about_window, text="3. The functionality of rainfall-runoff model implemented as a data-driven model, also exists, with inputs being a .mat formatted precipitation data, delineated watershed formatted as a .mat file and discharge data formatted as an excel file.")
    asgn2_2.grid(row=2, sticky=W)

    asgn3 = Label(about_window, text="4. DQT plot can be generated, for low-flow analysis, by supplying a .mat precipitation file, .mat delineated watershed file, and discharge data as an excel file, D and T values.")
    asgn3.grid(row=3, sticky=W)

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
    if fileObj is not None:
        filename = fileObj.name
        extension = findExtension(filename)
        if extension == 'shp':
            file_name_sv.set(filename)
        else:
            messagebox.showerror("error", "The file selected was not a .shp file.")

def gen_mask(curr_window):
    shp_fname = file_name_sv.get()
    mask_fname = mask_file_name_sv.get()

    ext = findExtension(shp_fname)
    if ext == 'shp':
        assignment1.giveMask(shp_fname, mask_fname)
        curr_window.destroy()
    else:
        messagebox.showerror("error", "The file selected was not a .shp file.")
    
def get_mask_name():
    dir_name = filedialog.asksaveasfilename(filetypes=(("Mask as png", "*.png"), ("All Files","*.*")), title="Enter file name..")
    mask_file_name_sv.set(dir_name)

def shapeToMask():
    new_window = Toplevel(top)
    new_window.resizable(True, True)

    txt = Label(new_window, text="Choose a shape file")
    txt.grid(row=0, column=0)

    global file_name_sv
    file_name_sv = StringVar()
    txt_entry = Entry(new_window, width=100, textvariable=file_name_sv)
    txt_entry.grid(row=0, column=1)

    browse_button = Button(new_window, text="Browse..", command=get_file)
    browse_button.grid(row=0, column=2)
    
    txt2 = Label(new_window, text="Choose a file to save mask file into...")
    txt2.grid(row=1, column=0)
 
    global mask_file_name_sv
    mask_file_name_sv = StringVar()
    txt2_entry = Entry(new_window, textvariable=mask_file_name_sv, width=100)
    txt2_entry.grid(row=1, column=1)

    take_mask_name_button = Button(new_window, text="Browse...", command=get_mask_name)
    take_mask_name_button.grid(row=1, column=2)

    gen_mask_file = Button(new_window, text="Generate Mask files...", command=lambda: gen_mask(new_window))
    gen_mask_file.grid(row=2, column=0, columnspan=3)

    new_window.mainloop()

def delineate_watershed():
    new_window = Toplevel(top)
    new_window.resizable(True, True)

    txt1 = Label(new_window, text="Choose a .tif DEM data-set...")
    txt1.grid(row=0, column=0)

    global dem_fname
    dem_fname = StringVar()
    entry_1 = Entry(new_window, width=100, textvariable=dem_fname)
    entry_1.grid(row=0, column=1)

    # line no. 155 for get_DEM_data
    browse_button = Button(new_window, text="Browse..", command=get_DEM_data)
    browse_button.grid(row=0, column=2)

    txt2 = Label(new_window, text="Choose a file to save the delineated watershed into...")
    txt2.grid(row=1, column=0)

    global del_shed_fname
    del_shed_fname = StringVar()
    entry_2 = Entry(new_window, width=100, textvariable=del_shed_fname)
    entry_2.grid(row=1, column=1)

    # line no. 167 for save_watershed_data
    browse_button2 = Button(new_window, text="Browse..", command=save_watershed_data)
    browse_button2.grid(row=1, column=2)

    #line 171 has start_delineation
    confirm_button = Button(new_window, text="Delineate", command=lambda: start_delineation(new_window))
    confirm_button.grid(row=2, column = 0, columnspan= 3)

def get_DEM_data():
    cwd = os.getcwd()
    fileObj = filedialog.askopenfile(initialdir=cwd,
                           filetypes =(("DEM dataset .tif file", "*.tif"),("All Files","*.*")),
                           title = "Choose a file.")
    if fileObj is not None:
        file_name = fileObj.name
        extension = findExtension(file_name)
        if extension == 'tif':
            dem_fname.set(file_name)
        else:
            messagebox.showerror("error", "File chosen was not a .tif file")

def save_watershed_data():
    dir_name = filedialog.asksaveasfilename(filetypes=(("delineated watershed as .mat", "*.mat"), ("All Files","*.*")), title="Enter file name..")
    del_shed_fname.set(dir_name)

def start_delineation(curr_window):
    dem_data = dem_fname.get()
    save_fname = del_shed_fname.get()

    ext1, ext2 = findExtension(dem_data), findExtension(save_fname)

    if ext1 == 'tif' and ext2 == 'mat':
        # start executing delineation.py
        # destroy window
        # curr_window.destroy()
    else:
        messagebox.showerror("error", "Please check your input files")

# set booleans for checking validity of input files 
# for environmental flow task
check_basin_mat, check_precip_mat = False, False
check_delineated_mat, check_limits_mat = False, False

def environment_flows():
    ''' take input files from user '''
    new_window = Toplevel(top)
    new_window.resizable(True, True)

    txt1 = Label(new_window, text="Choose a .mat precipitation file...")
    txt1.grid(row=0, column=0, columnspan = 2)

    txt2 = Label(new_window, text="Choose a .mat delineated file...")
    txt2.grid(row=1, column=0, columnspan = 2)

    txt3 = Label(new_window, text="Choose a .xls discharge file...")
    txt3.grid(row=2, column=0, columnspan = 2)


    global v1 
    v1 = StringVar()
    e1 = Entry(new_window, textvariable=v1, width=100)
    e1.grid(row=0, column=2, columnspan = 2)


    global v2
    v2 = StringVar()
    e2 = Entry(new_window, textvariable=v2, width=100)
    e2.grid(row=1, column=2, columnspan = 2)

    global v3
    v3 = StringVar()
    e3 = Entry(new_window, textvariable=v3, width=100)
    e3.grid(row=2, column=2, columnspan = 2)


    browse_button1 = Button(new_window, text="Browse..", command=lambda: is_mat_valid(1))
    browse_button1.grid(row=0, column=4)

    browse_button2 = Button(new_window, text="Browse..", command=lambda: is_mat_valid(2))
    browse_button2.grid(row=1, column=4)

    browse_button3 = Button(new_window, text="Browse..", command=lambda: is_mat_valid(3))
    browse_button3.grid(row=2, column=4)

    D_LABEL = Label(new_window, text="Input D value")
    D_LABEL.grid(row=3, column = 0)

    global D_VAL
    D_VAL = StringVar()
    D_ENTRY = Entry(new_window, textvariable=D_VAL, width=10)
    D_ENTRY.grid(row=3, column=1, sticky=W, padx=1)

    T_LABEL = Label(new_window, text="Input T value")
    T_LABEL.grid(row=3, column = 2, sticky=E)

    global T_VAL
    T_VAL = StringVar()
    T_ENTRY = Entry(new_window, textvariable=T_VAL, width=10)
    T_ENTRY.grid(row=3, column=3, sticky=W, padx=0)

    b4_reg_label = Label(new_window, text="Input the image name to save DQT plot before regression")
    b4_reg_label.grid(row=4, column = 0, columnspan = 2)

    global fname_b4_reg
    fname_b4_reg = StringVar()
    b4_reg_entry = Entry(new_window, textvariable=fname_b4_reg, width=100)
    b4_reg_entry.grid(row=4, column = 2, columnspan = 2)

    browse_save_loc_b4_reg = Button(new_window, text="Browse..", command=lambda: fetch_dir_name(0))
    browse_save_loc_b4_reg.grid(row=4, column=4)

    after_reg_label = Label(new_window, text="Input the image name to save DQT plot after regression")
    after_reg_label.grid(row=5, column = 0, columnspan = 2)

    global fname_after_reg
    fname_after_reg = StringVar()
    after_reg_entry = Entry(new_window, textvariable=fname_after_reg, width=100)
    after_reg_entry.grid(row=5, column = 2, columnspan = 2)

    browse_save_loc_after_reg = Button(new_window, text="Browse..", command=lambda: fetch_dir_name(1))
    browse_save_loc_after_reg.grid(row=5, column=4)


    submit_button = Button(new_window, text="Get Flows...", command=lambda: start_asgn3([v1, v2, v3],[D_VAL, T_VAL], [fname_b4_reg, fname_after_reg], new_window))
    submit_button.grid(row=6, columnspan=5)

    if check_basin_mat and check_delineated_mat and check_limits_mat and check_precip_mat:
        new_window.mainloop()

def fetch_dir_name(check_val):
    dir_name = filedialog.asksaveasfilename(filetypes=(("DQT Plot as png", "*.png"), ("All Files","*.*")), title="Enter file name..")
    if check_val == 0:
        fname_b4_reg.set(dir_name)
    else:
        fname_after_reg.set(dir_name)

def start_asgn3(l1, l2, l3, win):
    ''' take arguments from the environmental flows window, 
    i.e. the StringVars , check validity and if valid, start executing assignment3 code'''

    # l1 contains list of input files, namely the basin.mat, precipitation.mat, delineated.mat
    # and the limits.mat

    a1, a2, a3 = l1[0], l1[1], l1[2]
    precip_file = a1.get()
    delineated_file = a2.get()
    discharge_file = a3.get()

    # l2 contains the user-desired D and T values
    d = l2[0].get()
    t = l2[1].get()

    # l3 contains the file names for the DQT plots to be saved 
    fname_b4_reg, fname_after_reg = l3[0].get(), l3[1].get()

    ext1 = findExtension(precip_file)
    ext2 = findExtension(delineated_file)
    ext3 = findExtension(discharge_file)

    ext_b4 = findExtension(fname_b4_reg)
    ext_after = findExtension(fname_after_reg)

    if ext1 == "mat" and ext2 == "mat"  and ext3 == "xls" and t.isnumeric() and t.isnumeric() \
        and ext_b4 == "png" and ext_after == "png":
        assignment_3.get_flow(precip_file, delineated_file, discharge_file, d, t, fname_b4_reg, fname_after_reg)
        win.destroy()
    else:
        messagebox.showerror("error", "The file selected was not a .mat/.xls file, or the D or T values are non-numeric")

def is_mat_valid(param):
    cwd = os.getcwd()
    file_type = ""
    if param == 1:
        file_type = "Precipitation .mat File"
    elif param == 2:
        file_type = "Delineated .mat File"
    elif param == 3:
        file_type = "Discharge .xls file"

    if param == 1 or param == 2:
        fileObj = filedialog.askopenfile(initialdir=cwd,
                           filetypes =((file_type, "*.mat"),("All Files","*.*")),
                           title = "Choose a file.")
    elif param == 3:
        fileObj = filedialog.askopenfile(initialdir=cwd,
                           filetypes =((file_type, "*.xls"),("All Files","*.*")),
                           title = "Choose a file.")

    if fileObj is not None:
        filename = fileObj.name
        extension = findExtension(filename)
        if extension == 'mat':
            if param == 1:
                v1.set(filename)
            elif param == 2:
                v2.set(filename)
        elif extension == "xls" and param == 3:
                v3.set(filename)
        else:
            messagebox.showerror("error", "The file selected was not a proper .mat file.")


options = Menu(menubar, tearoff=0)
options.add_command(label="Generate Mask file...", command=shapeToMask)
options.add_command(label="Generate Environmental Flows...", command=environment_flows)
options.add_command(label="Delineate Watershed...", command=delineate_watershed)
#options.add_command(label="Get Predicted runoff values...", command)
menubar.add_cascade(label="Options", menu=options)

help = Menu(menubar, tearoff=0)  
help.add_command(label="About", command=about)  
menubar.add_cascade(label="Help", menu=help)  


top.config(menu=menubar)  
top.mainloop()  