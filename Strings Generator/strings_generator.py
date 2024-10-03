import os
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rules_processor.log"),
        logging.StreamHandler()
    ]
)

CONFIG_FILE = 'config.json'
LANGUAGES = ['en', 'de', 'es', 'fr', 'pt-br', 'ru', 'zh-cn']

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def process_rules_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Updated regex patterns
    id_match = re.search(r'ID\s*=\s*([a-zA-Z0-9_.]+)', content, re.IGNORECASE)
    name_key_match = re.search(r'NameKey\s*=\s*"([^"]+)"', content, re.IGNORECASE)
    icon_key_match = re.search(r'IconNameKey\s*=\s*"([^"]+)"', content, re.IGNORECASE)
    description_key_match = re.search(r'DescriptionKey\s*=\s*"([^"]+)"', content, re.IGNORECASE)

    entries = []

    if id_match and name_key_match and icon_key_match:
        id_value = id_match.group(1)
        name_key = name_key_match.group(1)
        icon_key = icon_key_match.group(1)
        description_key = description_key_match.group(1) if description_key_match else None

        # Extract the last part after '/'
        name_entry = name_key.split("/")[-1]
        icon_entry = icon_key.split("/")[-1]
        description_entry = description_key.split("/")[-1] if description_key else None

        # Format the output with a comment for the ID and proper spacing
        entry = f'\n\t// {id_value}\n'
        entry += f'\t{name_entry}\t\t\t= "{name_entry}"\n'
        entry += f'\t{icon_entry}\t\t= "{icon_entry}"\n'
        if description_entry:
            entry += f'\t{description_entry}\t= "{description_entry}"\n'

        entries.append(entry)
        logging.info(f"Processed file: {file_path}")
    else:
        missing = []
        if not id_match:
            missing.append("ID")
        if not name_key_match:
            missing.append("NameKey")
        if not icon_key_match:
            missing.append("IconNameKey")
        logging.warning(f"Missing keys in file: {file_path}. Missing: {', '.join(missing)}")

    return entries

def process_rules_directory(root_path):
    entries = []
    for root, dirs, files in os.walk(root_path):
        logging.debug(f"Searching in directory: {root}")
        for file_name in files:
            if file_name.endswith('.rules'):
                file_path = os.path.join(root, file_name)
                logging.debug(f"Processing file: {file_path}")
                entries += process_rules_file(file_path)
    return entries

def process_rules_directory_with_log(root_path):
    entries = []
    log = ""
    for root, dirs, files in os.walk(root_path):
        log += f"Searching in directory: {root}\n"
        for file_name in files:
            if file_name.endswith('.rules'):
                file_path = os.path.join(root, file_name)
                log += f"Processing file: {file_path}\n"
                file_entries = process_rules_file(file_path)
                if file_entries:
                    entries += file_entries
                else:
                    log += f"Skipped file (missing keys): {file_path}\n"
    return entries, log

def select_mod_file():
    file_path = filedialog.askopenfilename(
        title="Select mod.rules file",
        filetypes=[("Rules files", "*.rules")],
        initialdir=os.getcwd()
    )
    if file_path:
        root_dir = os.path.dirname(file_path)
        config = load_config()
        config['root_dir'] = root_dir
        save_config(config)
        entries, log = process_rules_directory_with_log(root_dir)
        if entries:
            display_output(entries, log)
        else:
            messagebox.showinfo("No Entries", "No valid entries found in the selected mod.rules file.")

def display_output(entries, log=None):
    output_window = tk.Toplevel()
    output_window.title("Generated .rules Entries")

    output_text = scrolledtext.ScrolledText(output_window, wrap=tk.WORD, width=80, height=25)
    output_text.pack(padx=10, pady=10)
    output_text.insert(tk.END, "Parts\n{\n")
    
    for entry in entries:
        output_text.insert(tk.END, entry)
    
    output_text.insert(tk.END, "}\n")

    if log:
        log_label = tk.Label(output_window, text="Processing Log:")
        log_label.pack(pady=(10,0))
        log_text = scrolledtext.ScrolledText(output_window, wrap=tk.WORD, width=80, height=10)
        log_text.pack(padx=10, pady=5)
        log_text.insert(tk.END, log)
        log_text.configure(state='disabled')

    # Save buttons frame
    buttons_frame = tk.Frame(output_window)
    buttons_frame.pack(pady=10)

    save_buttons = {}
    for lang in LANGUAGES:
        btn = tk.Button(buttons_frame, text=f"Save as {lang}.rules", 
                        command=lambda l=lang, e=entries: save_to_file(e, l))
        btn.pack(side=tk.LEFT, padx=2)
        save_buttons[lang] = btn

    # Save All button
    save_all_button = tk.Button(output_window, text="Save All Languages", 
                                command=lambda e=entries: save_all_languages(e))
    save_all_button.pack(pady=5)

def get_strings_folder(root_dir):
    strings_folder = os.path.join(root_dir, 'strings')
    if not os.path.exists(strings_folder):
        os.makedirs(strings_folder)
    return strings_folder

def save_to_file(entries, language):
    config = load_config()
    root_dir = config.get('root_dir')
    if not root_dir:
        messagebox.showerror("Error", "Root directory not found in config.")
        return

    strings_folder = get_strings_folder(root_dir)
    file_name = f"{language}.rules"
    file_path = os.path.join(strings_folder, file_name)

    if os.path.exists(file_path):
        result = messagebox.askyesno("File Exists", 
                                     f"{file_name} already exists. Do you want to save it as a different name?")
        if not result:
            return
        else:
            new_file_name = filedialog.asksaveasfilename(
                title="Save As",
                defaultextension=".rules",
                filetypes=[("Rules files", "*.rules")],
                initialdir=strings_folder
            )
            if not new_file_name:
                return
            file_path = new_file_name

    content = "Parts\n{\n"
    for entry in entries:
        content += entry
    content += "}\n"

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    messagebox.showinfo("Success", f"File saved successfully as {os.path.basename(file_path)}!")

def save_all_languages(entries):
    config = load_config()
    root_dir = config.get('root_dir')
    if not root_dir:
        messagebox.showerror("Error", "Root directory not found in config.")
        return

    strings_folder = get_strings_folder(root_dir)
    for language in LANGUAGES:
        file_name = f"{language}.rules"
        file_path = os.path.join(strings_folder, file_name)

        if os.path.exists(file_path):
            result = messagebox.askyesno("File Exists", 
                                         f"{file_name} already exists. Do you want to save it as a different name?")
            if not result:
                continue
            else:
                new_file_name = filedialog.asksaveasfilename(
                    title=f"Save {language}.rules As",
                    defaultextension=".rules",
                    filetypes=[("Rules files", "*.rules")],
                    initialdir=strings_folder,
                    initialfile=language
                )
                if not new_file_name:
                    continue
                file_path = new_file_name

        content = "Parts\n{\n"
        for entry in entries:
            content += entry
        content += "}\n"

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        messagebox.showinfo("Success", f"File saved successfully as {os.path.basename(file_path)}!")

def create_ui():
    root = tk.Tk()
    root.title("Rules Generator")
    root.geometry("400x200")
    
    label = tk.Label(root, text="Select the mod.rules file:")
    label.pack(pady=20)

    select_button = tk.Button(root, text="Select mod.rules", command=select_mod_file)
    select_button.pack(pady=10)

    # Optionally, add a button to load from config
    config = load_config()
    if 'root_dir' in config:
        load_button = tk.Button(root, text="Load from Config", 
                                command=lambda: display_output(process_rules_directory(config['root_dir'])))
        load_button.pack(pady=5)

    root.mainloop()

# Run the UI
if __name__ == "__main__":
    create_ui()
