
# EasyGridLocations: A Cosmoteer Modding Tool

**EasyGridLocations** is a graphical tool that makes complex `.rules` part editing for [Cosmoteer](https://cosmoteer.net/) fast, visual, and hopefully error-free.  
No more hand-writing door locations, blocked cells, overlays, or ports—just click, export, and paste!

---

## 🟢 Recommended: Just Download the EXE!

1. **Get the latest EasyGridLocations.exe** from [Releases](./releases).
2. Double-click to run! No Python, additional setup, or dependencies.
3. The tool will open instantly—just start creating your grid locations.

*The EXE includes all required resources, images, and icons.*

---

## 🛠️ Want to Build or Run From Source?

If you’d rather generate your own EXE or run from Python source, follow the steps below:

### 1. Clone This Repository

```bash
git clone <repository-url>
cd <repository-folder>
````

### 2. Setup (Windows)

* Run `setup.bat` to auto-install everything in a virtualenv.
* Then launch `run.bat` to start the tool.

### 3. Manual Install (Mac/Linux/Python)

```bash
python -m venv venv
venv\Scripts\activate        # or: source venv/bin/activate
pip install -r requirements.txt
python EasyGridLocations.py
```

---

## Modes & Functionality

EasyGridLocations currently has **4 main modes**, each to help streamline Cosmoteer part creation.

---

### 1. Doors & Paths

**Set allowed door locations and block internal travel cells with a click.**
**Export:** `AllowedDoorLocations` & `BlockedTravelCells`

> ![Doors & Paths Screenshot Placeholder](screenshots/doors_paths_placeholder.png)

---

### 2. Blocked Travel Directions

**Visually set which sides of each cell are blocked (up, down, left, right) for precise pathing.**
**Export:** `BlockedTravelCellDirections`

> ![Blocked Directions Screenshot Placeholder](screenshots/blocked_dirs_placeholder.png)

---

### 3. Locations

**Click to add precisely placed points, graphics, or crew locations on your part.**

* *Supports fractions, rotation, relative/absolute placement, and layering.* - Visual Layering has more features coming soon.
* **Export:** Named blocks for overlays and crew positions (with or without verbose commented out code as needed)

> ![Locations Screenshot Placeholder](screenshots/locations_placeholder.png)

---

### 4. Thermal Ports

**New for Meltdown: Enable or disable custom thermal/heat ports for your part.**
**Export:** `Port_Thermal_*` rules blocks automatically optimized with inheritance (with or without verbose commented out code as needed)

> ![Thermal Ports Screenshot Placeholder](screenshots/thermal_ports_placeholder.png)

---

## Usage Overview

1. Set your grid/part size. And select a base image (e.g., floor.png)
2. Choose a mode (Doors & Paths, Blocked Cell Directions, Locations, Thermal Ports).
3. Click cells and use dialogs to set up your locations.
4. Copy individual blocks of code (per mode selected) or copy/save all the output code for your `.rules` file.

---

## Requirements (for Source/Developers)

* **Python 3.10+**
* **PySide6**

All dependencies auto-installed via `setup.bat` or `pip install -r requirements.txt`.
*End-users do not need Python if using the EXE.*

---

## For Developers & Contributors

* PRs, bug reports, and feature requests are welcome.
* Please check and update screenshots in the `/screenshots` directory as features evolve.

---

## License

This project is MIT licensed—see [LICENSE](LICENSE) for details.

---

*EasyGridLocations is not affiliated with or endorsed by Cosmoteer or Walternate Realities.
Made for the Cosmoteer modding community <3 by Rojamahorse*

