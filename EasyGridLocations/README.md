# EasyGrid Locations, A Cosmoteer Modding Tool

This tool helps create and manage door locations, blocked travel cells, and other part properties for Cosmoteer modding. The tool provides a user-friendly grid-based interface that allows you to configure your parts dynamically and generate the correct configuration code.

## Features

- Dynamically generates grids based on part size
- Allows easy toggling of door locations, blocked travel cells, and more
- Outputs properly formatted code for your Cosmoteer `.rules` files
- Copy generated code to the clipboard for easy insertion

### Prerequisites

Git & Python 3.10 or later

## Quick Setup & Updates (Windows)

For quick installation and usage of the tool, follow these steps:

### 1. Download the Tool

1. Clone or download this repository to your local machine:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

### 2. Run the Setup Script to Install or Update Dependencies

1. In the folder where you downloaded the repository, double-click the **`setup.bat`** file to automatically:
   - Set up a Python virtual environment.
   - Install the necessary dependencies.

> **Note**: If Python is not installed on your system, the script will prompt you to install Python. You can download it from the [official Python website](https://www.python.org/downloads/).

### 3. Run the Tool

1. Once the setup is complete, double-click the **`run.bat`** file to launch the EasyGridLocations tool.
2. The tool's GUI will open, and you can begin using it to configure door locations and blocked travel cells for your Cosmoteer mod.

### Additional Notes

- **Virtual Environment**: The setup script automatically creates and manages a Python virtual environment to keep dependencies isolated.
- **Requirements**: The tool requires Python 3.x. If you don’t have Python installed, the setup script will notify you.

By following these quick setup steps, you’ll be able to get started with the tool without needing to install dependencies manually!


## Manual Installation

To set up this tool, follow the steps below:

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Set Up a Virtual Environment

We recommend setting up a virtual environment to keep the dependencies for this project isolated.

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

This will install all the necessary Python packages to run the tool.

### 4. Run the Script

Once everything is set up, you can run the script with the following command:

```bash
python EasyGridLocations.py
```

This will launch the GUI tool, allowing you to configure your mod parts and generate code.

## Usage

1. **Grid Configuration**: Enter the X and Y size of your part and click **Submit Size** to generate the grid.
   ![image](https://github.com/user-attachments/assets/552db685-c6fa-4ade-ae46-73bd7d7dcfdb)

2. **Toggle Cells**: Click on cells in the grid to toggle door locations or blocked travel cells.
   ![image](https://github.com/user-attachments/assets/ac937489-7cbc-48b2-885c-396044e957d3)
   
3. **Generate Code**: Once your grid is configured, click **Generate Code** to get the correctly formatted output.
   ![image](https://github.com/user-attachments/assets/b9c8174d-125a-4576-a4b5-e832ebba5820)

4. **Copy to Clipboard**: Use the **Copy to Clipboard** button to copy the generated code for easy insertion into your `.rules` files.
  IMPORTANT: Remember to remove the PhysRects portion as that is still WIP.  
   ![image](https://github.com/user-attachments/assets/e7a0952f-0674-4802-aff4-bd47654d67ea)

## Requirements

The tool is built with Python and uses the following dependencies:
- **Tkinter** (for the GUI)
- **Pyperclip** (for clipboard operations)

These dependencies will be installed automatically when you run `pip install -r requirements.txt`.

## Additional Notes

- Make sure you have Python 3.x installed. You can download the latest version from [Python's official website](https://www.python.org/downloads/).
- Ensure you have Git installed on your system. You can download Git from [Git's official website](https://git-scm.com/downloads).
- If you run into any issues, feel free to open an issue in this repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```


