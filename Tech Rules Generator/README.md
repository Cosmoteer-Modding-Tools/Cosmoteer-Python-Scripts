# TechRulesGenerator

TechRulesGenerator is a Python-based GUI tool designed to help modders create `techs.rules` entries for their Cosmoteer mods efficiently. This tool parses your existing mod files to extract necessary information and assists in generating the appropriate code snippets for your tech rules.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage Instructions](#usage-instructions)
  - [Step 1: Select Mod Root (mod.rules File)](#step-1-select-mod-root-modrules-file)
  - [Step 2: Generate or Select techs.rules File](#step-2-generate-or-select-techsrules-file)
  - [Step 3: Select Part File](#step-3-select-part-file)
  - [Step 4: Setup techs.rules for Your Selected Part](#step-4-setup-techsrules-for-your-selected-part)
  - [Step 5: Generate Part Code](#step-5-generate-part-code)
- [Additional Features](#additional-features)
  - [Show techs.rules Readout](#show-techsrules-readout)
  - [Resetting the Tool](#resetting-the-tool)
- [Notes](#notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- **Automatic Parsing**: Reads your `mod.rules` and part files to extract necessary IDs and EditorGroups.
- **Prerequisite Selection**: Allows you to select prerequisites from a list of available parts in your mod.
- **Parts Unlocked Selection**: Enables selection of parts that will be unlocked by the tech.
- **Code Generation**: Generates the code snippet for your techs.rules entry, which can be copied to clipboard or saved to a file.
- **Scaffolding Generation**: Can generate a basic `techs.rules` file scaffold if one doesn't exist.

## Prerequisites

- **Python 3.6 or higher**: Make sure Python is installed on your system.
- **Required Python Packages**:
  - `tkinter`: Should come pre-installed with Python on most systems.
  - `pyperclip`: For clipboard functionality.
    ```bash
    pip install pyperclip
    ```

## Installation

1. **Clone or Download the Repository**: Download the script to your local machine.

2. **Install Required Packages**:
   ```bash
   pip install pyperclip
   ```

3. **Ensure tk is Installed**:
   - On Windows and macOS, `tkinter` is usually included.
   - On Linux, you may need to install it separately:
     ```bash
     sudo apt-get install python3-tk
     ```

## Usage Instructions

Run the script using Python:

```bash
python TechRulesGenerator.py
```

The tool will open a GUI window. Follow the steps below to use the tool effectively.

### Step 1: Select Mod Root (mod.rules File)

- **Purpose**: Specify the root directory of your mod by selecting the `mod.rules` file.
- **Action**:
  1. Click on the **Browse** button next to the mod.rules file path entry.
  2. Navigate to your mod's root directory and select the `mod.rules` file.
- **Notes**:
  - This step enables the tool to locate all relevant files within your mod.
  - After selecting, the tool will load prerequisite IDs from your mod.

### Step 2: Generate or Select techs.rules File

- **Purpose**: Specify where your `techs.rules` file is located or generate a new one.
- **Actions**:
  - **Generate techs.rules File**:
    1. Click on the **Generate techs.rules File** button.
    2. The tool will create a scaffold `techs.rules` file in `modes/career/` within your mod.
    3. Instructions will be provided in the scaffold file on how to include it in your `mod.rules`.
  - **Select Existing techs.rules File**:
    1. Click on the **Browse** button next to the techs.rules file path entry.
    2. Navigate to and select your existing `techs.rules` file.
- **Notes**:
  - The generated `techs.rules` file includes comments and instructions.
  - Ensure you include the necessary snippet in your `mod.rules` to activate the `techs.rules` file.

### Step 3: Select Part File

- **Purpose**: Choose the part file for which you want to create a tech entry.
- **Action**:
  1. Click on the **Browse** button next to the Part file path entry.
  2. Navigate to and select the `.rules` file of the part.
- **Notes**:
  - The tool will parse this file to extract the Part ID and EditorGroups.
  - Ensure the part file is correctly formatted and accessible.

### Step 4: Setup techs.rules for Your Selected Part

- **Purpose**: Configure details for your tech entry based on the selected part.
- **Actions**:
  - **Part ID**:
    - Auto-generated from the Part file.
    - Verify that it matches your expectations.
  - **Editor Groups**:
    1. A list of EditorGroups from the part file will be displayed.
    2. Select one or more EditorGroups that apply to your tech.
- **Notes**:
  - EditorGroups determine where the part appears in the editor.
  - If the part file uses `EditorGroup` (singular), only one can be selected.

### Step 5: Generate Part Code

- **Purpose**: Input additional details and generate the tech entry code.
- **Actions**:
  - **Prerequisite IDs**:
    1. Click on **Select Prerequisites**.
    2. In the pop-up window, select one or more prerequisites from the list.
    3. Click **Select** to confirm.
  - **Parts Unlocked**:
    1. Click on **Select Parts Unlocked**.
    2. In the pop-up window, select the parts that will be unlocked by this tech.
    3. Click **Select** to confirm.
    4. By default, the current part ID is selected.
  - **Cost**:
    - Enter the cost (in credits) for the tech.
- **Generate the Code**:
  1. After filling in all fields, click on **Generate Part Code**.
  2. The generated code will appear in a text box below.
- **Notes**:
  - Ensure all required fields are filled before generating.
  - The tool computes relative paths automatically for the generated code.

## Additional Features

### Show techs.rules Readout

- **Purpose**: View the current content of your `techs.rules` file.
- **Action**:
  - Click on the **Show techs.rules Readout** button.
  - A new window will display the contents.
- **Notes**:
  - Useful for verifying existing entries or copying code snippets.

### Resetting the Tool

- **Purpose**: Clear all fields and start over.
- **Action**:
  - Click on the **Reset** button at the bottom of the window.
- **Notes**:
  - This will clear all entries except for the mod root path and techs.rules path.
  - Use this when switching to a new part or making significant changes.

## Notes

- **Config File**: The tool creates a `config.ini` file to store paths and settings.
  - This allows for persistence between sessions.
- **Relative Paths**: The tool computes relative paths based on the location of the `techs.rules` file.
  - Ensure your mod structure is consistent to avoid path issues.
- **Error Messages**: The tool provides error messages for missing or incorrect inputs.
  - Read them carefully to resolve any issues.

## Troubleshooting

- **Cannot Import tkinter**:
  - Ensure that `tkinter` is installed on your system.
  - On Linux, you may need to install it via your package manager.
- **pyperclip Not Found**:
  - Install it using `pip install pyperclip`.
- **EditorGroups Not Extracted**:
  - Verify that your part file contains `EditorGroup` or `EditorGroups`.
  - Ensure the syntax in your part file matches expected formats.
- **Multiple "Step 5" Labels Appearing**:
  - This issue has been addressed in the latest version.
  - Ensure you are using the updated script provided.
- **Generated Code Has Incorrect Paths**:
  - Check that the mod root and part paths are correctly set.
  - The relative path computation depends on accurate inputs.

## License

This project is licensed under the MIT License. Feel free to modify and distribute as per the license terms.

---

*For any further assistance or to report issues, please contact the developer or submit an issue on the project's repository.*