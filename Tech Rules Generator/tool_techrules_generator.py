import tkinter as tk
from tkinter import messagebox, filedialog
import pyperclip
import os
import configparser
import re

class TechRulesGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Techs Rules Generator")
        self.geometry("1000x800")  # Adjusted window size

        # Initialize configuration
        self.config_file = "config.ini"
        self.config = configparser.ConfigParser()

        # Placeholder for dynamic fields
        self.dynamic_fields = {}

        # Initialize prerequisite IDs list
        self.prerequisite_ids = []

        # Initialize editor groups plural flag
        self.is_editorgroups_plural = False

        # Load configuration
        self.load_config()

        # Set up the scrollable main frame
        self.setup_scrollable_main_frame()

        # Step 1: Select Mod Root (mod.rules File)
        self.setup_step1()

        # Step 2: Generate or Select techs.rules File
        self.setup_step2()

        # Step 3: Select Part File
        self.setup_step3()

        # Button to show techs.rules readout
        self.setup_show_techrules_button()

        # Step 4: Parse Part File for ID and EditorGroups
        self.setup_step4()

        # Step 5: Generate Part Code
        self.setup_part_fields()

        # Reset Button
        self.setup_reset_button()

        # Load previously saved paths
        self.load_saved_paths()

    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config['Paths'] = {}
            self.config['Prerequisites'] = {}

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def setup_scrollable_main_frame(self):
        # Create a canvas and a vertical scrollbar for scrolling
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.v_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # Add the scrollable frame to the canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

    def setup_step1(self):
        # Step 1 Frame
        self.step1_frame = tk.Frame(self.scrollable_frame)
        self.step1_frame.pack(fill='x', padx=10, pady=10)

        self.step1_title = tk.Label(self.step1_frame, text="Step 1: Select Mod Root (mod.rules File)", font=("Helvetica", 16, "bold"))
        self.step1_title.pack(anchor='w')

        # Mod Root Selection
        self.mod_root_label = tk.Label(self.step1_frame, text="Select your mod.rules file (Mod Root Directory):")
        self.mod_root_label.pack(anchor='w', pady=(5, 0))

        self.mod_root_entry = tk.Entry(self.step1_frame, width=80)
        self.mod_root_entry.pack(padx=10, pady=5, anchor='w')

        self.mod_root_browse_button = tk.Button(self.step1_frame, text="Browse", command=self.browse_mod_root)
        self.mod_root_browse_button.pack(pady=5, anchor='w')

        # Help text for Mod Root
        self.mod_root_help_label = tk.Label(self.step1_frame, text="Example: Select the mod.rules file located at your mod's root directory.", font=("Helvetica", 9, "italic"))
        self.mod_root_help_label.pack(anchor='w', padx=10)

    def setup_step2(self):
        # Step 2 Frame
        self.step2_frame = tk.Frame(self.scrollable_frame)
        self.step2_frame.pack(fill='x', padx=10, pady=10)

        self.step2_title = tk.Label(self.step2_frame, text="Step 2: Generate or Select techs.rules File", font=("Helvetica", 16, "bold"))
        self.step2_title.pack(anchor='w')

        # Generate techs.rules Button
        self.generate_techrules_button = tk.Button(self.step2_frame, text="Generate techs.rules File", command=self.generate_techs_rules, state='disabled')
        self.generate_techrules_button.pack(pady=10, anchor='w')

        # techs.rules File Selection
        self.techrules_label = tk.Label(self.step2_frame, text="Select the techs.rules file:")
        self.techrules_label.pack(anchor='w', pady=(5, 0))

        self.techrules_entry = tk.Entry(self.step2_frame, width=80)
        self.techrules_entry.pack(padx=10, pady=5, anchor='w')

        self.techrules_browse_button = tk.Button(self.step2_frame, text="Browse", command=self.browse_techrules, state='disabled')
        self.techrules_browse_button.pack(pady=5, anchor='w')

        # Help text for techs.rules path
        self.techrules_help_label = tk.Label(self.step2_frame, text="Example: modes/career/techs.rules within your mod.", font=("Helvetica", 9, "italic"))
        self.techrules_help_label.pack(anchor='w', padx=10)

    def setup_step3(self):
        # Step 3 Frame
        self.step3_frame = tk.Frame(self.scrollable_frame)
        self.step3_frame.pack(fill='x', padx=10, pady=10)

        self.step3_title = tk.Label(self.step3_frame, text="Step 3: Select Part File", font=("Helvetica", 16, "bold"))
        self.step3_title.pack(anchor='w')

        # Part File Selection
        self.part_label = tk.Label(self.step3_frame, text="Select the Part file:")
        self.part_label.pack(anchor='w', pady=(5, 0))

        self.part_entry = tk.Entry(self.step3_frame, width=80)
        self.part_entry.pack(padx=10, pady=5, anchor='w')

        self.part_browse_button = tk.Button(self.step3_frame, text="Browse", command=self.browse_part, state='disabled')
        self.part_browse_button.pack(pady=5, anchor='w')

        # Help text for Part path
        self.part_help_label = tk.Label(self.step3_frame, text="Example: ships/terran/weapons/small/discordmissile/dm_launcher.rules", font=("Helvetica", 9, "italic"))
        self.part_help_label.pack(anchor='w', padx=10)

    def setup_show_techrules_button(self):
        # Moved the show techrules button here
        self.show_techrules_button = tk.Button(self.scrollable_frame, text="Show techs.rules Readout", command=self.show_techrules, state='disabled')
        self.show_techrules_button.pack(pady=10)

    def setup_step4(self):
        # Step 4 Frame
        self.step4_frame = tk.Frame(self.scrollable_frame)
        self.step4_frame.pack(fill='x', padx=10, pady=10)

        self.step4_title = tk.Label(self.step4_frame, text="Step 4: Setup techs.rules for your selected Part", font=("Helvetica", 16, "bold"))
        self.step4_title.pack(anchor='w')

        # Part ID
        self.part_id_label = tk.Label(self.step4_frame, text="Part ID (auto-generated from Part file):")
        self.part_id_label.pack(anchor='w', pady=(5, 0))

        self.part_id_entry = tk.Entry(self.step4_frame, width=80, state='readonly')
        self.part_id_entry.pack(padx=10, pady=5, anchor='w')

        # EditorGroups
        self.editorgroups_label = tk.Label(self.step4_frame, text="Editor Groups:")
        self.editorgroups_label.pack(anchor='w', pady=(5, 0))

        self.editorgroups_listbox = tk.Listbox(self.step4_frame, selectmode=tk.MULTIPLE, width=60, height=10)
        self.editorgroups_listbox.pack(padx=10, pady=5, anchor='w')

        # Help text for EditorGroups
        self.editorgroups_help_label = tk.Label(self.step4_frame, text="Select one or more Editor Groups from the Part file.", font=("Helvetica", 9, "italic"))
        self.editorgroups_help_label.pack(anchor='w', padx=10)

    def setup_reset_button(self):
        self.reset_button = tk.Button(self.scrollable_frame, text="Reset", width=20, command=self.reset_fields)
        self.reset_button.pack(pady=10)

    def load_saved_paths(self):
        if self.config.has_section('Paths'):
            if self.config.has_option('Paths', 'mod_root'):
                mod_root = self.config.get('Paths', 'mod_root')
                self.mod_root_entry.insert(0, os.path.join(mod_root, 'mod.rules'))
                # Enable dependent buttons
                self.generate_techrules_button.config(state='normal')
                self.techrules_browse_button.config(state='normal')
                self.part_browse_button.config(state='normal')
                # Load prerequisite IDs
                self.load_prerequisite_ids(mod_root)
            if self.config.has_option('Paths', 'techrules_path'):
                self.techrules_entry.insert(0, self.config.get('Paths', 'techrules_path'))
            if self.config.has_option('Paths', 'part_id'):
                self.part_id_entry.config(state='normal')
                self.part_id_entry.delete(0, tk.END)
                self.part_id_entry.insert(0, self.config.get('Paths', 'part_id'))
                self.part_id_entry.config(state='readonly')
            if self.config.has_option('Paths', 'editorgroups'):
                # Populate the listbox with saved editor groups
                editorgroups = self.config.get('Paths', 'editorgroups').split(',')
                for group in editorgroups:
                    self.editorgroups_listbox.insert(tk.END, group)
                # Select all editor groups by default
                self.editorgroups_listbox.select_set(0, tk.END)

    def browse_mod_root(self):
        file_path = filedialog.askopenfilename(
            title="Select mod.rules File",
            filetypes=[("Rules Files", "mod.rules"), ("All Files", "*.*")]
        )
        if file_path:
            if not os.path.basename(file_path).lower() == 'mod.rules':
                messagebox.showerror("Error", "Selected file is not 'mod.rules'. Please select the correct file.")
                return
            mod_root = os.path.dirname(os.path.abspath(file_path))
            self.mod_root_entry.delete(0, tk.END)
            self.mod_root_entry.insert(0, file_path)
            self.config['Paths']['mod_root'] = mod_root
            self.save_config()
            # Enable dependent buttons
            self.generate_techrules_button.config(state='normal')
            self.techrules_browse_button.config(state='normal')
            self.part_browse_button.config(state='normal')
            # Load prerequisite IDs immediately
            self.load_prerequisite_ids(mod_root)

    def browse_techrules(self):
        mod_root = self.config.get('Paths', 'mod_root', fallback=None)
        initial_dir = mod_root if mod_root else '/'
        file_path = filedialog.askopenfilename(
            title="Select techs.rules File",
            filetypes=[("Rules Files", "*.rules"), ("All Files", "*.*")],
            initialdir=initial_dir
        )
        if file_path:
            self.techrules_entry.delete(0, tk.END)
            self.techrules_entry.insert(0, file_path)
            self.config['Paths']['techrules_path'] = file_path
            self.save_config()

    def browse_part(self):
        mod_root = self.config.get('Paths', 'mod_root', fallback=None)
        initial_dir = mod_root if mod_root else '/'
        file_path = filedialog.askopenfilename(
            title="Select Part File",
            filetypes=[("Rules Files", "*.rules"), ("All Files", "*.*")],
            initialdir=initial_dir
        )
        if file_path:
            self.part_entry.delete(0, tk.END)
            self.part_entry.insert(0, file_path)
            self.parse_part_file()

    def parse_part_file(self):
        """Parse the selected Part file to extract ID and EditorGroups."""
        part_path = self.part_entry.get()
        if not part_path:
            return

        if not os.path.exists(part_path):
            messagebox.showerror("Error", f"Part file does not exist at: {part_path}")
            return

        try:
            with open(part_path, 'r') as file:
                content = file.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read Part file: {e}")
            return

        # Parse Part ID
        part_id = self.extract_field(content, 'ID')
        if part_id:
            self.part_id_entry.config(state='normal')
            self.part_id_entry.delete(0, tk.END)
            self.part_id_entry.insert(0, part_id)
            self.part_id_entry.config(state='readonly')
            self.config['Paths']['part_id'] = part_id
            self.save_config()
        else:
            messagebox.showerror("Error", "Failed to extract 'ID' from Part file.")
            return

        # Parse EditorGroups
        editorgroups, is_plural = self.extract_editorgroups(content)
        self.is_editorgroups_plural = is_plural  # Store whether plural or singular
        if editorgroups:
            self.editorgroups_listbox.delete(0, tk.END)
            for group in editorgroups:
                self.editorgroups_listbox.insert(tk.END, group)
            # Save editor groups to config
            self.config['Paths']['editorgroups'] = ','.join(editorgroups)
            self.save_config()
            # Select all editor groups by default
            self.editorgroups_listbox.select_set(0, tk.END)
        else:
            messagebox.showerror("Error", "Failed to extract 'EditorGroup' or 'EditorGroups' from Part file.")

        # Enable generate button
        self.show_techrules_button.config(state='normal')

    def extract_field(self, content, field_name):
        """Extract the value of a given field from the content."""
        pattern = rf"^\s*{field_name}\s*=\s*\"?([^\n\"]+)\"?"
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            # Return the first match, stripping any comments or trailing content
            value = matches[0].split('//')[0].strip()
            return value
        return None

    def extract_editorgroups(self, content):
        """Extract EditorGroup or EditorGroups from the Part file content."""
        # Try to find EditorGroups array
        pattern_plural = r"EditorGroups\s*=\s*\[([^\]]+)\]"
        match_plural = re.search(pattern_plural, content, re.IGNORECASE)
        if match_plural:
            groups = match_plural.group(1).split(',')
            groups = [grp.strip().strip('"').split('//')[0].strip() for grp in groups]
            return groups, True  # Return True for plural

        # Try to find single EditorGroup
        pattern_singular = r"EditorGroup\s*=\s*\"?([^\n\"]+)\"?"
        match_singular = re.search(pattern_singular, content, re.IGNORECASE)
        if match_singular:
            group = match_singular.group(1).split('//')[0].strip()
            return [group], False  # Return False for singular

        return [], False  # Default to empty list and False

    def setup_part_fields(self):
        # Part Fields Frame
        self.part_fields_frame = tk.Frame(self.scrollable_frame)
        self.part_fields_frame.pack(fill='x', padx=10, pady=10)

        # Prerequisite IDs
        self.dynamic_fields['prerequisites_label'] = tk.Label(self.part_fields_frame, text="Prerequisite IDs:")
        self.dynamic_fields['prerequisites_label'].pack(anchor='w', padx=10, pady=(5, 0))

        self.dynamic_fields['prerequisites_entry'] = tk.Entry(self.part_fields_frame, width=80)
        self.dynamic_fields['prerequisites_entry'].pack(padx=10, pady=(5, 0))

        self.dynamic_fields['prerequisites_button'] = tk.Button(self.part_fields_frame, text="Select Prerequisites", command=self.open_prerequisite_dialog)
        self.dynamic_fields['prerequisites_button'].pack(pady=5)

        # Parts Unlocked
        self.dynamic_fields['partsunlocked_label'] = tk.Label(self.part_fields_frame, text="Parts Unlocked:")
        self.dynamic_fields['partsunlocked_label'].pack(anchor='w', padx=10, pady=(5, 0))

        self.dynamic_fields['partsunlocked_entry'] = tk.Entry(self.part_fields_frame, width=80)
        self.dynamic_fields['partsunlocked_entry'].pack(padx=10, pady=(5, 0))

        self.dynamic_fields['partsunlocked_button'] = tk.Button(self.part_fields_frame, text="Select Parts Unlocked", command=self.open_partsunlocked_dialog)
        self.dynamic_fields['partsunlocked_button'].pack(pady=5)

        # Cost
        self.dynamic_fields['cost_label'] = tk.Label(self.part_fields_frame, text="Cost:")
        self.dynamic_fields['cost_label'].pack(anchor='w', padx=10, pady=(5, 0))

        self.dynamic_fields['cost_entry'] = tk.Entry(self.part_fields_frame, width=80)
        self.dynamic_fields['cost_entry'].pack(padx=10, pady=(5, 0))

        # Move the Step 5 label here, before the generate button
        self.part_fields_title = tk.Label(self.part_fields_frame, text="Step 5: Generate Part Code", font=("Helvetica", 16, "bold"))
        self.part_fields_title.pack(anchor='w', pady=(20, 5))

        # Generate Button
        self.dynamic_fields['generate_button'] = tk.Button(self.part_fields_frame, text="Generate Part Code", command=self.generate_part_code)
        self.dynamic_fields['generate_button'].pack(pady=10)

    def generate_part_code(self):
        techrules_path = self.techrules_entry.get()
        part_path = self.part_entry.get()
        part_id = self.part_id_entry.get()

        prerequisites = self.dynamic_fields['prerequisites_entry'].get().strip()
        cost = self.dynamic_fields['cost_entry'].get().strip()

        parts_unlocked_str = self.dynamic_fields['partsunlocked_entry'].get().strip()
        if parts_unlocked_str:
            parts_unlocked_list = [part.strip() for part in parts_unlocked_str.split(',') if part.strip()]
        else:
            parts_unlocked_list = [part_id]  # Default to the current part ID

        if not all([techrules_path, part_path, part_id, cost]):
            messagebox.showerror("Error", "Please ensure all required fields are filled.")
            return

        # Compute relative path from techs.rules directory to Part file
        techrules_dir = os.path.dirname(techrules_path)
        try:
            relative_path = os.path.relpath(part_path, techrules_dir).replace("\\", "/")
        except Exception as e:
            messagebox.showerror("Error", f"Error computing relative path: {e}")
            return

        # Handle EditorGroups
        selected_indices = self.editorgroups_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one Editor Group.")
            return

        total_editorgroups = self.editorgroups_listbox.size()
        if self.is_editorgroups_plural:
            if len(selected_indices) == total_editorgroups:
                # All editor groups selected
                editorgroup_field = f"EditorGroups = &<{relative_path}>/Part/EditorGroups"
            elif len(selected_indices) == 1:
                # Single Editor Group selected
                index = selected_indices[0]
                editorgroup_field = f"EditorGroup = &<{relative_path}>/Part/EditorGroups/{index}"
            else:
                # Multiple but not all editor groups selected
                editorgroup_paths = [f"&<{relative_path}>/Part/EditorGroups/{idx}" for idx in selected_indices]
                editorgroup_field = f"EditorGroups = [{', '.join(editorgroup_paths)}]"
        else:
            # Part file has singular EditorGroup
            if len(selected_indices) == 1:
                editorgroup_field = f"EditorGroup = &<{relative_path}>/Part/EditorGroup"
            else:
                messagebox.showerror("Error", "Cannot select multiple Editor Groups when Part file has single 'EditorGroup'.")
                return

        # Format PartsUnlocked
        parts_unlocked_formatted = f"[{', '.join(parts_unlocked_list)}]"

        # Format Prerequisites
        prerequisites_formatted = ""
        if prerequisites:
            prerequisites_list = [prereq.strip() for prereq in prerequisites.split(',') if prereq.strip()]
            prerequisites_formatted = f"    Prerequisites = [{', '.join(prerequisites_list)}]\n"

        # Final Output
        formatted_output = f"""
{{
    ID = {part_id}
    NameKey = &<{relative_path}>/Part/NameKey
    DescriptionKey = &<{relative_path}>/Part/DescriptionKey
    Icon = &<{relative_path}>/Part/EditorIcon
    {editorgroup_field}
    PartsUnlocked = {parts_unlocked_formatted}
{prerequisites_formatted}    Cost = {cost}
}}
"""
        self.display_output(formatted_output.strip())

    def display_output(self, formatted_output):
        # Create or clear the output text box
        if 'output_text' not in self.dynamic_fields:
            self.dynamic_fields['output_text'] = tk.Text(self.scrollable_frame, height=25, width=120)
            self.dynamic_fields['output_text'].pack(padx=10, pady=10)
        else:
            self.dynamic_fields['output_text'].delete(1.0, tk.END)

        # Insert the formatted output
        self.dynamic_fields['output_text'].insert(tk.END, formatted_output)

        # Create or enable Copy and Save buttons
        if 'copy_button' not in self.dynamic_fields:
            button_frame = tk.Frame(self.scrollable_frame)
            button_frame.pack(pady=10)
            self.dynamic_fields['copy_button'] = tk.Button(button_frame, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(formatted_output))
            self.dynamic_fields['copy_button'].pack(side='left', padx=5)
            self.dynamic_fields['save_button'] = tk.Button(button_frame, text="Save as File", command=lambda: self.save_to_file(formatted_output))
            self.dynamic_fields['save_button'].pack(side='left', padx=5)

    def reset_fields(self):
        # Clear Part-related entries
        self.part_entry.delete(0, tk.END)
        self.part_id_entry.config(state='normal')
        self.part_id_entry.delete(0, tk.END)
        self.part_id_entry.config(state='readonly')
        self.editorgroups_listbox.delete(0, tk.END)
        self.clear_dynamic_fields()

        # Disable dependent buttons
        self.show_techrules_button.config(state='disabled')

        # Remove output fields if they exist
        if 'output_text' in self.dynamic_fields:
            self.dynamic_fields['output_text'].pack_forget()
            del self.dynamic_fields['output_text']
        if 'copy_button' in self.dynamic_fields:
            self.dynamic_fields['copy_button'].pack_forget()
            del self.dynamic_fields['copy_button']
        if 'save_button' in self.dynamic_fields:
            self.dynamic_fields['save_button'].pack_forget()
            del self.dynamic_fields['save_button']

        # Re-setup the part fields
        self.setup_part_fields()

    def clear_dynamic_fields(self):
        for widget in self.dynamic_fields.values():
            widget.pack_forget()
        self.dynamic_fields.clear()

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "Text copied to clipboard!")

    def save_to_file(self, text):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(text)
                messagebox.showinfo("Saved", f"File saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def show_techrules(self):
        techrules_path = self.techrules_entry.get()

        if not techrules_path:
            messagebox.showerror("Error", "Please select the techs.rules file first.")
            return

        # Compute absolute path of techs.rules file
        techrules_abs = os.path.abspath(techrules_path)
        if not os.path.exists(techrules_abs):
            messagebox.showerror("Error", f"techs.rules file does not exist at: {techrules_abs}")
            return

        # Read techs.rules file
        try:
            with open(techrules_abs, 'r') as file:
                content = file.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read techs.rules file: {e}")
            return

        # Display the content in a new window
        popup = tk.Toplevel(self)
        popup.title("Current techs.rules Readout")
        popup.geometry("1000x800")

        text_box = tk.Text(popup, wrap='word')
        text_box.pack(expand=True, fill='both', padx=10, pady=10)

        text_box.insert(tk.END, content)

    def open_prerequisite_dialog(self):
        """Open a dialog that allows users to select prerequisite IDs from a list."""
        # Ensure mod root is determined
        mod_root = self.config.get('Paths', 'mod_root', fallback=None)
        if not mod_root:
            messagebox.showerror("Error", "Mod root could not be determined. Please select the mod.rules file first.")
            return

        if not self.prerequisite_ids:
            messagebox.showerror("Error", "No Part IDs found in the mod.")
            return

        # Create a new pop-up window
        popup = tk.Toplevel(self)
        popup.title("Select Prerequisite IDs")
        popup.geometry("400x500")

        # Instructions
        instructions = tk.Label(popup, text="Select Prerequisite IDs from your mod:")
        instructions.pack(pady=10)

        # Listbox with multiple selection
        self.prereq_listbox = tk.Listbox(popup, selectmode=tk.MULTIPLE, width=50, height=20)
        self.prereq_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Populate the listbox
        for idx, prereq in enumerate(self.prerequisite_ids):
            self.prereq_listbox.insert(tk.END, prereq)

        # Pre-select already selected prerequisites
        current_prereq = self.dynamic_fields.get('prerequisites_entry', tk.Entry(self)).get().strip()
        if current_prereq:
            selected = [pr.strip() for pr in current_prereq.split(',') if pr.strip()]
            for i, prereq in enumerate(self.prerequisite_ids):
                if prereq in selected:
                    self.prereq_listbox.select_set(i)

        # Buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        select_button = tk.Button(button_frame, text="Select", command=lambda: self.set_prerequisites(popup))
        select_button.pack(side=tk.LEFT, padx=5)

    def load_prerequisite_ids(self, mod_root):
        """Scan all .rules files in the mod root to collect Part IDs."""
        part_ids = []
        for root, dirs, files in os.walk(mod_root):
            for file in files:
                if file.endswith(".rules"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                    except:
                        continue

                    # Check if file defines a Part
                    if re.search(r'^\s*Part\s*:', content, re.MULTILINE):
                        # Extract Part IDs
                        ids = re.findall(r'^\s*ID\s*=\s*\"?([^\n\"]+)\"?', content, re.MULTILINE)
                        for id_value in ids:
                            id_value = id_value.split('//')[0].strip()
                            part_ids.append(id_value)

        self.prerequisite_ids = sorted(set(part_ids))
        # Save to config
        self.config['Prerequisites']['part_ids'] = ','.join(self.prerequisite_ids)
        self.save_config()

    def set_prerequisites(self, popup):
        """Set the selected prerequisites in the prerequisites entry."""
        selected_indices = self.prereq_listbox.curselection()
        selected_ids = [self.prerequisite_ids[i] for i in selected_indices]
        prerequisites_str = ', '.join(selected_ids)

        # Set the prerequisites in the entry field
        self.dynamic_fields['prerequisites_entry'].delete(0, tk.END)
        self.dynamic_fields['prerequisites_entry'].insert(0, prerequisites_str)

        # Close the pop-up
        popup.destroy()

    def open_partsunlocked_dialog(self):
        """Open a dialog that allows users to select parts to unlock."""
        # Ensure mod root is determined
        mod_root = self.config.get('Paths', 'mod_root', fallback=None)
        if not mod_root:
            messagebox.showerror("Error", "Mod root could not be determined. Please select the mod.rules file first.")
            return

        if not self.prerequisite_ids:
            messagebox.showerror("Error", "No Part IDs found in the mod.")
            return

        # Create a new pop-up window
        popup = tk.Toplevel(self)
        popup.title("Select Parts Unlocked")
        popup.geometry("400x500")

        # Instructions
        instructions = tk.Label(popup, text="Select Parts Unlocked from your mod:")
        instructions.pack(pady=10)

        # Listbox with multiple selection
        parts_listbox = tk.Listbox(popup, selectmode=tk.MULTIPLE, width=50, height=20)
        parts_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Populate the listbox
        for idx, part in enumerate(self.prerequisite_ids):
            parts_listbox.insert(tk.END, part)

        # Pre-select already selected parts
        current_parts = self.dynamic_fields.get('partsunlocked_entry', tk.Entry(self)).get().strip()
        if current_parts:
            selected = [pr.strip() for pr in current_parts.split(',') if pr.strip()]
            for i, part in enumerate(self.prerequisite_ids):
                if part in selected:
                    parts_listbox.select_set(i)

        # Ensure current part ID is selected by default
        current_part_id = self.part_id_entry.get()
        if current_part_id:
            for i, part in enumerate(self.prerequisite_ids):
                if part == current_part_id:
                    parts_listbox.select_set(i)
                    break

        # Buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        select_button = tk.Button(button_frame, text="Select", command=lambda: self.set_partsunlocked(parts_listbox, popup))
        select_button.pack(side=tk.LEFT, padx=5)

    def set_partsunlocked(self, parts_listbox, popup):
        """Set the selected parts in the partsunlocked entry."""
        selected_indices = parts_listbox.curselection()
        selected_parts = [self.prerequisite_ids[i] for i in selected_indices]
        partsunlocked_str = ', '.join(selected_parts)

        # Set the partsunlocked in the entry field
        self.dynamic_fields['partsunlocked_entry'].delete(0, tk.END)
        self.dynamic_fields['partsunlocked_entry'].insert(0, partsunlocked_str)

        # Close the pop-up
        popup.destroy()

    def generate_techs_rules(self):
        mod_root = self.config.get('Paths', 'mod_root', fallback=None)
        if not mod_root:
            messagebox.showerror("Error", "Mod root is not set. Please select your mod.rules file first.")
            return

        # Define the path for techs.rules
        techs_rules_dir = os.path.join(mod_root, 'modes', 'career')
        techs_rules_path = os.path.join(techs_rules_dir, 'techs.rules')

        # Check if techs.rules already exists
        if os.path.exists(techs_rules_path):
            messagebox.showwarning("Warning", f"techs.rules already exists at: {techs_rules_path}. It will not be overwritten.")
            return

        # Create modes/career/ directory if it doesn't exist
        os.makedirs(techs_rules_dir, exist_ok=True)

        # Define the scaffolding content
        scaffolding = """//AutoGenerated by TechRulesGenerator

//Instructions: Uncomment and add the following snippet to your mod.rules file to activate this file:

// +++++++++ vv insert below in mod.rules vv ++++++++++ //
// Adding Techs to Career Mode
/*{
    Action = AddMany
    AddTo = "<./Data/modes/career/techs.rules>/Techs"
    ManyToAdd = &<modes/career/techs.rules>/Techs
}*/
// +++++++++ ^^ insert above in mod.rules ^^ ++++++++++ //

Techs
[


    /*
//Example Category

    {
        ID = author.part2
        NameKey = &<../../example/examplepart/part.rules>/Part/NameKey
        DescriptionKey = &<../../example/examplepart/part.rules>/Part/DescriptionKey
        Icon = &<../../example/examplepart/part.rules>/Part/EditorIcon
        EditorGroup = &<../../example/examplepart/part.rules>/Part/EditorGroups/0
        PartsUnlocked = [author.part2]
        //Prerequisites = [author.part1]
        Cost = 500
    }
    */
//Energy Weapons Category

//Projectile Weapons Category

//Defenses Category

//Flight Category

//Crew Category

//Power Category

//Production Category

//Storage Category

//Utilities Category

//Structure Category
]
"""

        # Write the scaffolding to techs.rules
        try:
            with open(techs_rules_path, 'w') as file:
                file.write(scaffolding)
            messagebox.showinfo("Success", f"techs.rules has been created at: {techs_rules_path}")
            # Automatically populate the techrules_entry field
            self.techrules_entry.delete(0, tk.END)
            self.techrules_entry.insert(0, techs_rules_path)
            self.config['Paths']['techrules_path'] = techs_rules_path
            self.save_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create techs.rules file: {e}")

if __name__ == "__main__":
    app = TechRulesGenerator()
    app.mainloop()
