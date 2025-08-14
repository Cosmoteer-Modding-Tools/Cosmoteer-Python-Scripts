
# Cosmoteer Image Destroyer: A Cosmoteer Texture Damage Tool

**Cosmoteer Image Destroyer** is a small GUI tool for Cosmoteer modding that “physically” damages an image: it punches real holes (alpha cut-outs), burns pixels, and sprinkles scorches and shrapnel on top — all driven by your own tileable stencils and stamps (don't worry some are already included).

- Holes are cut only where your base image is non-transparent.
- Hole covers are pasted into the cutouts with matching rotation and tile alignment.
- Scorches/shrapnel never appear over empty (fully transparent) pixels.

---

## 🟢 Recommended: Just Download the EXE!

1. Grab **ImageDestroyer.exe** from Releases.
2. Double-click to run — no Python needed.
3. Drop your assets in the `assets/` folder next to the EXE.

*The EXE bundles includes resources and looks for your assets via the included data folders.*

---

## Run From Source

### 1) Setup (Windows)

```bat
setup.bat
run.bat
````

`setup.bat` creates/activates a local `venv`, upgrades pip, and installs deps from `requirements.txt`.

### 2) Manual (Mac/Linux/Python)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python damage_painter.py
```

## Folder Layout & Assets

```
project/
  damage_painter.py
  run.bat
  setup.bat
  requirements.txt
  imagedestroyer.ico
  default_images/
    imagedestroyer_splash.png
  assets/
    hole_punch/
      A_33.png  A_66.png  ...   (64px, opaque = HOLE, transparent = no hole)
    hole_covers/
      A_33.png  A_66.png  ...   (64px, must match names/orientation)
    scorches/
      Scorch_1.png Scorch_2.png ... (128px stamps; scaled <= 1.0)
    shrapnel/
      ... (optional, same as scorches)
```

**Dynamic loading:** Add or remove files at will; the app scans these folders at runtime.
**Naming for levels:** `*_33.png` and `*_66.png` are detected automatically. Level **50** splits hole density between `_33` and `_66`.

---

## Defaults

* **33**: holes 0.20, scorches 0.20, shrapnel 0.10
* **50**: holes 0.30, scorches 0.30, shrapnel 0.15
* **66**: holes 0.40, scorches 0.50, shrapnel 0.20
* Rim width **0**, rim darkness **0** (off by default)
* Scorches: severity **0.90**, min scale **0.50**, max **1.00**, rotation **180**
* Shrapnel: severity **0.85**, min scale **0.05**, max **0.30**, rotation **180**

**Saving:** default filename is `<original>_<level>.png` (e.g., `floor_33.png`).

---

## Requirements (for Source/Developers)

* **Python 3.10+**
* **PySide6**
* **Pillow**

All installed by `setup.bat`.

---

## Using Cosmoteer Image Destroyer
Image Destroyer lets you “damage” a sprite by punching real holes (alpha cut-outs), burning the edges, and sprinkling scorches/shrapnel — all driven by tile stencils you control.

### 1) Start & drag-and-drop (screenshot 1)

**Launch** the app.
**Drag & drop** a PNG onto the large preview area, or click Load Base… and pick a file.
*The app remembers your last Load/Save folder between runs.*

<div align="center">
<img width="1184" height="800" alt="Figure 1 - Start screen" src="https://github.com/user-attachments/assets/f4053bf3-4616-4239-a0ed-a448825671b2" />
<br>  
<i>Figure 1 — Start screen: drag a PNG into the preview or use Load Base….</i>
<br>
</div>


### 2) Pick a damage preset (screenshot 2)

Use **Damage level** to select 33, 50, or 66.

This controls default densities and which hole stencils are used:
```
* 33 → uses *_33.png stencils
* 50 → mixes *_33.png + *_66.png
* 66 → uses *_66.png stencils
```

Number Sliders auto-populate to sane defaults (you can tweak anytime):
```
* Holes: Tile density (default: 33→0.20, 50→0.30, 66→0.40).
* Holes only affect pixels that were already opaque in your base.

* Scorches: Density & Severity (defaults: density per level; severity 0.90; min scale 0.50; max 1.00; rot 180°).
* Scorches never land over empty (transparent) pixels.

* Shrapnel: Optional layer with its own density/severity (defaults: severity 0.85; min 0.05; max 0.30; rot 180°).
```
  
<div align="center"> 
<img width="1186" height="797" alt="Figure 2 - Damage presets" src="https://github.com/user-attachments/assets/9866bf6a-ec98-442e-a3e3-21e9ccd436d4" />
<br>
<i>Figure 2 — Damage presets: switching between _33 and _66 adjusts density and picks matching stencils.</i>
  <br>
</div>

### 3) Save with auto filename (screenshot 3)

Click **Save** Result….

*The dialog proposes <original>_<level>.png (e.g., floor_33.png, floor_66.png, floor_50.png) in your last save folder.*

You can change the name/location as needed; the image saves as PNG with real transparency.
<div align="center"> 
<img width="1194" height="796" alt="Figure 3 - Save dialog" src="https://github.com/user-attachments/assets/0a0ba416-9561-41e3-8e6b-a1a0c89453ab" />
<br>
<i>Figure 3 — Save dialog: auto-suggested name includes the selected level suffix.</i>
  <br>
</div>
---

## License

MIT. See `LICENSE`.

*Not affiliated with Cosmoteer or Walternate Realities.*


I do this for fun but if you feel compelled to support development you may do so by scanning the QR code or clicking the button below. 

<div align="center">

  <a href="https://buymeacoffee.com/arojassunt" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-red.png" alt="Buy Me a Coffee" style="width: 160px;">
  </a>
  <br>
  <img width="160" height="160" alt="bmc_qr_rojamahorse" src="https://github.com/user-attachments/assets/4c419e1a-7333-4cc5-83c2-d26bfccb519d" />
  
</div>
---
