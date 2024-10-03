import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Function to process each rules file and extract NameKey and IconNameKey
def process_rules_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find ID, NameKey, and IconNameKey
    id_match = re.search(r'ID\s*=\s*(SW\.[^\s]+)', content)
    name_key_match = re.search(r'NameKey\s*=\s*"([^"]+)"', content)
    icon_key_match = re.search(r'IconNameKey\s*=\s*"([^"]+)"', content)

    entries = []

    if id_match and name_key_match and icon_key_match:
        id_value = id_match.group(1)
        name_key = name_key_match.group(1)
        icon_key = icon_key_match.group(1)

        # Format the output with a comment for the ID and proper spacing
        entry = (f'\n\t// {id_value}\n'
                 f'\t{name_key.split("/")[-1]}\t\t\t= "{name_key.split("/")[-1]}"\n'
                 f'\t{icon_key.split("/")[-1]}\t\t= "{icon_key.split("/")[-1]}"\n')

        entries.append(entry)

    return entries

# Function to process all .rules files in a selected directory and generate output
def process_rules_directory(directory_path):
    entries = []
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith('.rules'):
                file_path = os.path.join(root, file_name)
                entries += process_rules_file(file_path)

    return entries

# Function to open directory dialog
def select_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        entries = process_rules_directory(directory_path)
        if entries:
            display_output(entries)

# Function to display the output in a scrollable text box
def display_output(entries):
    output_window = tk.Toplevel()
    output_window.title("Generated .rules Entries")

    output_text = scrolledtext.ScrolledText(output_window, wrap=tk.WORD, width=80, height=25)
    output_text.pack(padx=10, pady=10)
    output_text.insert(tk.END, "Parts\n{\n")
    
    for entry in entries:
        output_text.insert(tk.END, entry)
    
    output_text.insert(tk.END, "}\n")

    save_button = tk.Button(output_window, text="Save to File", command=lambda: save_to_file(output_text.get("1.0", tk.END)))
    save_button.pack(pady=10)

# Function to save the generated output to a file
def save_to_file(content):
    file_path = filedialog.asksaveasfilename(defaultextension=".rules", filetypes=[("Rules files", "*.rules")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        messagebox.showinfo("Success", "File saved successfully!")

# Set up the UI
def create_ui():
    root = tk.Tk()
    root.title("en.rules Generator")
    root.geometry("400x200")
    
    label = tk.Label(root, text="Select the folder containing .rules files:")
    label.pack(pady=10)

    select_button = tk.Button(root, text="Select Folder", command=select_directory)
    select_button.pack(pady=20)

    root.mainloop()

# Run the UI
create_ui()
