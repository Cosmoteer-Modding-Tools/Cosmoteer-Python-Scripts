
# SymLinkCreator

## Overview

The **SymLinkCreator** is a Python script with a graphical user interface (GUI) designed to help you create symbolic links (symlinks) in bulk for files and/or folders. The script allows you to select an origin (either a single file or a folder) and a destination folder, and it will automatically create symlinks. The script also includes an option to toggle whether to include folders when creating symlinks from a folder origin.

## Requirements

Before using **SymLinkCreator**, make sure you have the following installed on your machine:

1. **Python 3.x** - You can download Python from the official website: [python.org](https://www.python.org/).
2. **Python `tkinter` Library** - This library is included with most standard Python installations.

## Setup Instructions

### 1. Install Python

If you haven't already, download and install Python from [python.org](https://www.python.org/). Ensure that Python is added to your system PATH during the installation process.

### 2. Running the Script

Once you have Python installed, follow these steps to use **SymLinkCreator**:

1. Navigate to the directory where both the `SymLinkCreator.bat` and `SymLinkCreator.py` files are located.
   
2. **Run the Batch File**:
   - On Windows, right-click the `SymLinkCreator.bat` file and select **"Run as Administrator"**.
   - The script requires elevated permissions to create symlinks, so running as Administrator is necessary.

   Alternatively, you can run the `.bat` file from the command line with elevated privileges by navigating to the folder and typing:
   
   ```sh
   SymLinkCreator.bat
   ```

## Using SymLinkCreator

### Step 1: Select Origin (File or Folder)

- You can either:
  - Click **"Browse Folder"** to select a folder as the origin.
  - Click **"Browse File"** to select a single file as the origin.
  
- If you choose a folder, all files within that folder (and optionally subfolders, depending on the toggle setting) will be processed to create symlinks.

### Step 2: Select Destination Folder

- Click **"Browse"** to select the destination folder where the symlinks will be created.

### Step 3: Toggle Folder Inclusion (Optional)

- If you selected a folder as the origin, you can choose whether or not to include subfolders when creating symlinks by toggling the **"Include Folders"** option.

### Step 4: Create Symlinks

- Once the origin and destination have been selected, click **"Create Symlinks"**. The script will process the selected files and folders, creating symlinks in the destination folder.

### Important Notes

- If you are creating symlinks for files inside a folder, ensure the **"Include Folders"** toggle is correctly set based on whether or not you want subfolders symlinked.
- The script will require **administrator privileges** to create symlinks on Windows, so always make sure to run the `.bat` file as Administrator.

## Troubleshooting

- **Permission Issues**: If you receive a permission error when creating symlinks (e.g., `WinError 1314: A required privilege is not held by the client`), make sure you are running the batch file with Administrator privileges.
  
- **Python Errors**: If Python is not installed or not recognized, verify that Python is installed and added to your system’s PATH.

## License

The **SymLinkCreator** is provided as-is, without any warranty. Use it at your own risk.

## Contribution

This project is provided for convenience. Feel free to fork the repository, submit pull requests, or make any modifications you need. If you’d like to support, consider donating to your favorite charity or sharing the tool with others! If you still feel compelled to contribute to me directly you can [venmo me a coffee](https://www.venmo.com/u/Rojamahorse)"# SymLink Creator" 
