```markdown
# Strings Generator

![Strings Generator Banner](https://via.placeholder.com/800x200?text=Rules+Generator+Banner)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output](#output)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

**Strings Generator** is a Python-based tool designed to streamline the process of extracting and generating string entries from `.rules` files within mod directories. Whether you're developing a new mod or managing existing ones, this tool automates the extraction of key elements such as `NameKey`, `IconNameKey`, and `DescriptionKey`, facilitating the creation of localized string files across multiple languages (no translations included).

## Features

- **Recursive Directory Traversal:** Automatically scans through all subdirectories to locate and process `.rules` files.
- **Flexible Parsing:** Extracts `NameKey`, `IconNameKey`, and `DescriptionKey` regardless of their position within the file.
- **Multi-language Support:** Generates string files for multiple languages including English, German, Spanish, French, Portuguese (Brazil), Russian, and Chinese (Simplified). (All Cosmoteer Natives)
- **User-Friendly Interface:** Simple GUI built with Tkinter for easy file selection and operation.
- **Comprehensive Logging:** Keeps detailed logs of processed files and any issues encountered.
- **Configurable Settings:** Saves user preferences for quick access in future sessions.
- **Error Handling:** Notifies users of missing keys or other issues during processing.

## Prerequisites

- **Python 3.7 or higher**: Ensure that Python is installed on your system. You can download it from the [official website](https://www.python.org/downloads/).

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/rules-generator.git
   ```

2. **Navigate to the Project Directory:**

   ```bash
   cd rules-generator
   ```

3. **(Optional) Create a Virtual Environment:**

   It's good practice to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Required Packages:**

   The script primarily uses standard Python libraries, so no additional packages are required. However, ensure that Tkinter is installed.

   - **For Windows and macOS:** Tkinter is usually included with Python installations.
   - **For Linux:** You might need to install it separately.

     ```bash
     sudo apt-get install python3-tk
     ```

## Usage

1. **Run the Script:**

   Navigate to the project directory and execute the script.

   ```bash
   python rules_generator.py
   ```

2. **Select the `mod.rules` File:**

   - Upon launching, the GUI will prompt you to select the `mod.rules` file.
   - Navigate to the root directory of your mod where the `mod.rules` file is located and select it.

   ![Select mod.rules](https://via.placeholder.com/600x400?text=Select+mod.rules+File)

3. **Process and Generate Entries:**

   - The script will recursively scan all subdirectories for `.rules` files.
   - Extracted entries will be displayed in a scrollable window.

4. **Save Generated String Files:**

   - Use the provided buttons to save the entries as `.rules` files for different languages.
   - You can choose to save individual language files or all supported languages at once.

   ![Save Options](https://via.placeholder.com/600x400?text=Save+Options)

## Configuration

The script uses a `config.json` file to store user preferences, such as the root directory of the mod. This file is automatically created and updated upon selecting a `mod.rules` file.

### Example `config.json`

```json
{
    "root_dir": "C:/Users/YourUserName/Saved Games/Cosmoteer/YourSteamID/Mods/YourModDirectory"
}
```

## Output

### Generated String Files

The output string files are organized within a `strings` folder located in the root directory of your mod. Each language has its own `.rules` file, e.g., `en.rules`, `de.rules`, etc.

#### Example `en.rules`

```plaintext
Parts
{
    XwingCannon           = "XwingCannon"
    XwingCannonIcon       = "XwingCannonIcon"
    XwingCannonDesc       = "XwingCannonDesc"
}
```

### Log File

A `rules_processor.log` file is generated in the script's directory, detailing the processing steps, including:

- Directories searched
- Files processed
- Any missing keys or errors encountered

## Logging

The script utilizes Python's built-in `logging` module to provide detailed logs of its operations. This is crucial for debugging and ensuring that all `.rules` files are processed correctly.

- **Log Levels:**
  - `DEBUG`: Detailed information, typically of interest only when diagnosing problems.
  - `INFO`: Confirmation that things are working as expected.
  - `WARNING`: An indication that something unexpected happened or indicative of some problem in the near future.
  - `ERROR`: Due to a more serious problem, the software has not been able to perform some function.

- **Log File Location:**

  The `rules_processor.log` file is located in the same directory as the script.

## Troubleshooting

### Common Issues

1. **No Entries Found:**

   - **Cause:** The selected `mod.rules` file or other `.rules` files might be missing required keys (`ID`, `NameKey`, `IconNameKey`).
   - **Solution:** Check the `rules_processor.log` file for details on which files are missing keys. Ensure that all `.rules` files contain the necessary keys.

2. **Script Doesn't Traverse All Directories:**

   - **Cause:** Permission issues or symbolic links causing `os.walk` to skip certain directories.
   - **Solution:** Ensure that the script has the necessary permissions to read all directories. Avoid using symbolic links within the mod directory.

3. **Encoding Errors:**

   - **Cause:** `.rules` files not encoded in UTF-8.
   - **Solution:** Ensure all `.rules` files are saved with UTF-8 encoding.

4. **Tkinter Not Found:**

   - **Cause:** Tkinter is not installed or not included in the Python installation.
   - **Solution:** Install Tkinter as per the [Prerequisites](#prerequisites) section.

### Getting Help

If you encounter issues not covered in this guide, feel free to [open an issue](https://github.com/Rojamahorse/Cosmoteer-Helper-Toolkit/issues) on the repository or contact the maintainer.

## Contributing

Contributions are welcome! Whether it's reporting bugs, suggesting features, or submitting pull requests, your input helps improve the project.

### Steps to Contribute

1. **Fork the Repository:**

   Click the "Fork" button at the top right of the repository page.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/Rojamahorse/Cosmoteer-Helper-Toolkit.git
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:**

   Implement your feature or fix.

5. **Commit Your Changes:**

   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Create a Pull Request:**

   Navigate to the original repository and create a pull request from your fork.

### Code of Conduct

Please adhere to the [Code of Conduct](https://github.com/Rojamahorse/Cosmoteer-Helper-Toolkit) in all interactions.

## License

This project is licensed under the [MIT License](https://github.com/Rojamahorse/Cosmoteer-Helper-Toolkit).

---

© 2024 [Rojamahorse](https://github.com/Rojamahorse)

```