# Cosmoteer Decal Namer

A small utility to help Cosmoteer modders generate and manage their decal upgrade lists in the new “Upgrades” block format. Instead of shipping multiple PNGs for each size or variation of the same decal, you can now map old names (and sizes) to a single “upgrade” decal, with optional rotation, flip and invert attributes. Note the game can only scale down so your replacement decal should always be larger than or equal to the original.

---

## Features

- **Generate an upgrade list** from a folder of decal image files.
- **Batch rename substitutions** for old or new decal IDs when generating the list.
- **Optional prefix**: enter a custom string to prepend to each new decal ID. NOTE: You will need to add that prefix to the decal PNG files as well.
- **Support for scaling**: map multiple old size variants (e.g. `A_64x`, `A_128x`, `A_256x`) to one single file, by specifying the `Rot0Size = [x, y]` you need.
- **Advanced attributes** (commented out by default):
  - `Rotation=<0–3>`  - specify the number of 90° rotations to apply to the decal.
  - `FlipX=true` / `FlipY=true`  - flip the decal horizontally or vertically.
  - `Invert=true`  - invert the transparent pixels to white and the white pixels to transparent.

---

## Prerequisites

- **Windows**, **macOS** or **Linux** with Python 3.8+ installed.
- The following Python packages (installed automatically by the setup script):
  - PySide6 – for the simple GUI
  - Pillow – for image filename parsing

---

## Installation

1. Place `decal_namer.py`, `setup.bat` and `run.bat` in the same folder.
2. Double-click **setup.bat** to create a `venv` in that folder and install dependencies.
3. Once setup finishes, use **run.bat** to launch the decal namer GUI.

---

## Usage

1. **Select your decal folder** – where all your `.png` files live.
2. (Optional) **Enter a Prefix**  
   - If you type e.g. `SW_`, every generated new decal ID will start with `SW_`.  
   - **Note**: this prefix is only applied to the generated list; you must still rename your actual PNG files on disk if you want them to match.
3. (Optional) **Add substitutions**  
   - Use “Find” / “Replace” fields to batch-rename any IDs on the fly.  
   - You can target either the **Old** list (to clean up legacy names) and/or the **New** list (to tweak your upgrade IDs before copying).
4. **Generate List**  
   - The script will scan all PNGs, infer your old IDs (filename without extension), and build an array of `{ Old="…"; New={ ID="…"; Rot0Size=[x,y]; /*…*/ }; }`.
5. **Copy & Paste**  
   - Copy the resulting block into your mod’s `.rules` file under the `Upgrades [ … ]` section.

---

## Background & Examples

Cosmoteer’s new decal format lets you **reuse one PNG** for multiple sizes or variations:

- **Before**:  
  Decal_A_64x.png, Decal_A_128x.png, Decal_A_256x.png

- **After**:  
  Only `Decal_A_256x.png` in your mod folder, with a list like:
  ```
  Upgrades 
  [
    { Old="Decal_A_64x";   New={ ID="Decal_A_256x"; Rot0Size=[1,1]; };
    { Old="Decal_A_128x";  New={ ID="Decal_A_256x"; Rot0Size=[1,1]; };
    { Old="Decal_A_256x";  New={ ID="Decal_A_256x"; Rot0Size=[1,1]; };
  ]
  ```

This way, you ship one file but support all three sizes at runtime.

---

## Advanced Attributes

You can uncomment and tweak these in each `New` block:

### Rotation
```
Rotation=1;  -- 0=0°, 1=90°, 2=180°, 3=270°
```

### FlipX / FlipY
```
FlipX=true;
FlipY=true;
```

### Invert
```
Invert=true;  -- invert the sprite transparency
```

Use these to avoid having separate PNGs for rotated or flipped variants.

---

## Troubleshooting & FAQ

- **Q:** “My actual file names don’t match my New IDs.”  
  **A:** The script only generates the list text. You’ll need to rename or copy the PNGs on disk yourself to match the New IDs you choose.

- **Q:** “Substitutions didn’t seem to apply.”  
  **A:** Check whether you’re editing the Old or New side—substitutions apply only to the side you select before running.

- **Q:** “I want a different default size.”  
  **A:** Manually edit the `Rot0Size` values in the generated block before copying.

---

## Contributing

Feel free to open issues or pull requests to:

- Add support for more image formats.
- Automate the actual PNG renaming.
- Export directly into `.rules` files.
- Improve the GUI layout or instructions.

---

Happy modding!
