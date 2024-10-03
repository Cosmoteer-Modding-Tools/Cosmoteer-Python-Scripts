import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes

def create_symlink(src, dest, is_folder):
    try:
        if is_folder:
            os.symlink(src, dest, target_is_directory=True)
        else:
            os.symlink(src, dest)
    except OSError as e:
        print(f"Error creating symlink from {src} to {dest}: {e}")

def check_admin():
    """ Check if the script is running with admin privileges on Windows. """
    try:
        is_admin = (os.name == 'nt') and ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    return is_admin

def select_origin_folder():
    origin_dir = filedialog.askdirectory(title="Select the Origin Folder (the folder you want to create a symlink for)")
    origin_path_var.set(origin_dir)

def select_origin_file():
    origin_file = filedialog.askopenfilename(title="Select the Origin File (the file you want to create a symlink for)")
    origin_path_var.set(origin_file)

def select_destination_folder():
    destination_dir = filedialog.askdirectory(title="Select the Destination Folder (where symlinks will be created)")
    destination_path_var.set(destination_dir)

def create_symlinks():
    origin = origin_path_var.get()
    destination = destination_path_var.get()
    include_folders = folder_toggle_var.get()

    if not origin or not destination:
        messagebox.showwarning("Missing Folders", "Please select both origin and destination.")
        return

    if not check_admin():
        messagebox.showwarning("Insufficient Privileges", "Please run the script as Administrator to create symlinks.")
        return

    if os.path.isfile(origin):  # If the origin is a single file
        symlink_path = os.path.join(destination, os.path.basename(origin))
        create_symlink(origin, symlink_path, False)
    elif os.path.isdir(origin):  # If the origin is a folder
        for item in os.listdir(origin):
            item_path = os.path.join(origin, item)
            symlink_path = os.path.join(destination, item)

            # Check if it's a folder and handle toggle
            if os.path.isdir(item_path) and not include_folders:
                continue

            create_symlink(item_path, symlink_path, os.path.isdir(item_path))

    messagebox.showinfo("Symlinks Created", "Symlinks have been created successfully.")

# Initialize the main window
root = tk.Tk()
root.title("Symlink Creator")

# Origin file/folder selection
tk.Label(root, text="Origin:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
origin_path_var = tk.StringVar()
tk.Entry(root, textvariable=origin_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)

tk.Button(root, text="Browse Folder", command=select_origin_folder).grid(row=0, column=2, padx=10, pady=5)
tk.Button(root, text="Browse File", command=select_origin_file).grid(row=0, column=3, padx=10, pady=5)

# Destination folder selection
tk.Label(root, text="Destination Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
destination_path_var = tk.StringVar()
tk.Entry(root, textvariable=destination_path_var, width=50).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_destination_folder).grid(row=1, column=2, padx=10, pady=5)

# Folder toggle option
folder_toggle_var = tk.BooleanVar()
folder_toggle_var.set(True)
tk.Checkbutton(root, text="Include Folders in Symlink Process", variable=folder_toggle_var).grid(row=2, column=1, padx=10, pady=5)

# Create symlink button
tk.Button(root, text="Create Symlinks", command=create_symlinks).grid(row=3, column=1, padx=10, pady=20)

# Start the Tkinter event loop
root.mainloop()
