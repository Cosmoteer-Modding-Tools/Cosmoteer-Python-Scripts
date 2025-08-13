
# TODO
# Quirks:
# 1) Adding Image to overlay should default a size rounded based on number of pixels.  E.g., 128x128px = 2, 2
# 1a) Loading Base Image doesn't auto input the correct location (e.g., middle), given the current UI, properties still show and if the user accidently hits "apply changes" they will accidently for it show up at 0,0 (which is the default)
# 2) Browsing for a file (Base Image or Image Overlay) should set the directory as default for the next browse.
# 3) Moving up and down doesn't dynamically change the layer its assigned to.  
# 4) Making any changes auto reassigns the layer to constructure structure for some reason?
# 5) Base Layer can be assigned to Floor by Default
# 6) Ideally a layer seperator should be defaulted to show in the layers menu allowing a user to easily see where they are dragging and droping the Z, something to the effect of:
#   Checkbox - ItemName
#   --- Floor ---
#   Checkbox - Item Name2
#   --- Roof ---
# 7) Output code should always have 'd' after rotation degree (e.g., 90d) 
# 8) Syntax needs fixing 
# 8a) Images should include Layer assignment e.g., 				Layer = "floors"
# 8b) Selecting Relative in the dialog should remove the location value of the item and assume location of the item it is nested to (picked from the layers menu) Output should be Offset = [x,y] - this will need to dynamically set to absolute and adjust to assume Location = "[x,y]" if "unnested" Note that Absolute / Relative toggles and Offset field should be included in properties menu for Images
# 8c) Example of Syntax for nested items w/offset
#		TurretGraphics
#		{
#			Type = Graphics
#			Location = [0, 0]
#			Rotation = 90d
#			OperationalDoodad
#			{
#				Layer = "turrets" 
#				Offset = [0, 2.625-(12/64)]
#				DamageLevels
#				[
#					{
#						File = "floor.png"
#						Size = [3, 3]
#					}
#				]
#			}
#			NonOperationalDoodad
#			{
#				Layer = "turrets" 
#				Offset = [0, 2.625]
#				DamageLevels
#				[
#					{
#						File = "gun_doodads_off.png"
#						Size = [1, 2]
#					}
#				]
#			}
#		}
# Enhancements: 
# 1) Changes done in properties should be realtimed to the canvas applying can save changes to the underlying code.  
# 2) Ability to nudge via arrow keys or UI directional pads (e.g., left/right/up/down)
# 3) Ability to zoom in on canvas for finetuning locations

#!/usr/bin/env python3
# EasyGridLocations_PySide6_v2.py
# Requires Python 3.10+ and PySide6>=6.0
import sys, os, math
from pathlib import Path
from fractions import Fraction

from PySide6.QtCore import Qt, QPointF, QThread
from PySide6.QtGui import (
    QBrush, QPen, QColor, QPixmap, QFont, QPainter, QFontMetricsF, QTransform, QGuiApplication
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QFileDialog, QComboBox,
    QDoubleSpinBox, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QSlider, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QSpinBox, QGroupBox, QPlainTextEdit, QSplashScreen, QAbstractItemView  
)

CELL_SIZE = 64
MAX_INTERIOR = 40 # max W or H of interior grid
ARROW_LEN = 20
INDENT = "\t"  # for indentation in code blocks

# --- Fixed layer types & their UniqueBucket Z --- (more can be added here)
LAYER_Z = {
    "structure_construction": -750,
    "floors":                -700,
    "turrets":               -600,
    "doodads_low":           -500,
    "walls_stencil":         -400,
    "external_walls":        -300,
    "walls":                 -200,
    "doors":                 -100,
    # (CREW renders here, between doors and weapons)
    "weapons":                  0,
    "doodads_high":           100,
    "lights_add":             200,
    "fire":                   300,
    "roofs":                 1000,
    "roof_doodads":          1100,
    "construction":          1150,
    "construction_delta":    1175,
    "roof_turrets":          1200,
    "roof_lights_fancy":     1300,
}
LAYER_TYPES = list(LAYER_Z.keys())
CREW_Z   = (LAYER_Z["doors"] + LAYER_Z["weapons"]) / 2.0  # -50
POINTS_Z = 9999  # keep points drawn on top in the editor

def parse_coord(s: str) -> float:
    """Parse decimal or fraction 'num/den' to float."""
    try:
        if '/' in s:
            return float(Fraction(s.strip()))
        return float(s)
    except Exception:
        return 0.0

def parse_size(s: str) -> float:
    """
    Accepts '2.5', '3/4', '1 7/64', '2 32/64', etc.
    Returns float (0.0 if invalid).
    """
    try:
        s = s.strip()
        if " " in s:  # mixed number: "<int> <num>/<den>"
            whole, frac = s.split(None, 1)
            return float(int(whole) + Fraction(frac))
        if "/" in s:  # pure fraction: "<num>/<den>"
            return float(Fraction(s))
        return float(s)  # decimal
    except Exception:
        return 0.0

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller .exe """
    import sys, os
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- Thermal Ports (all possible, vanilla order, commented out if disabled) ---
def vanilla_ports_all(W, H, port_status):
    ports = []
    if W == 1 and H == 1:
        for dirn in ["Up", "Right", "Down", "Left"]:
            enabled = port_status.get((0,0,dirn), False)
            name = f"Port_Thermal_{dirn}"
            ports.append((name, [0,0], dirn, enabled))
        return ports
    elif W == 2 and H == 2:
        order = [
            ("Port_Thermal_TopLeft",    [0,0], "Left"),
            ("Port_Thermal_LeftUp",     [0,0], "Up"),
            ("Port_Thermal_RightUp",    [1,0], "Up"),
            ("Port_Thermal_TopRight",   [1,0], "Right"),
            ("Port_Thermal_BottomRight",[1,1], "Right"),
            ("Port_Thermal_RightDown",  [1,1], "Down"),
            ("Port_Thermal_LeftDown",   [0,1], "Down"),
            ("Port_Thermal_BottomLeft", [0,1], "Left"),
        ]
        for name, loc, dirn in order:
            enabled = port_status.get(tuple(loc)+(dirn,), False)
            ports.append((name, loc, dirn, enabled))
        return ports
    else:
        # Corners (each gets two ports)
        ports.append(("Port_Thermal_TopLeft", [0,0], "Left", port_status.get((0,0,"Left"), False)))
        ports.append(("Port_Thermal_LeftUp", [0,0], "Up", port_status.get((0,0,"Up"), False)))
        ports.append(("Port_Thermal_TopRight", [W-1,0], "Right", port_status.get((W-1,0,"Right"), False)))
        ports.append(("Port_Thermal_RightUp", [W-1,0], "Up", port_status.get((W-1,0,"Up"), False)))
        ports.append(("Port_Thermal_BottomRight", [W-1,H-1], "Right", port_status.get((W-1,H-1,"Right"), False)))
        ports.append(("Port_Thermal_RightDown", [W-1,H-1], "Down", port_status.get((W-1,H-1,"Down"), False)))
        ports.append(("Port_Thermal_BottomLeft", [0,H-1], "Left", port_status.get((0,H-1,"Left"), False)))
        ports.append(("Port_Thermal_LeftDown", [0,H-1], "Down", port_status.get((0,H-1,"Down"), False)))
        # Top edge (excluding corners)
        for x in range(1, W-1):
            ports.append((f"Port_Thermal_MidUp{x}", [x,0], "Up", port_status.get((x,0,"Up"), False)))
        # Right edge (excluding corners)
        for y in range(1, H-1):
            ports.append((f"Port_Thermal_MidRight{y}", [W-1,y], "Right", port_status.get((W-1,y,"Right"), False)))
        # Bottom edge (excluding corners)
        for x in range(W-2, 0, -1):
            ports.append((f"Port_Thermal_MidDown{x}", [x,H-1], "Down", port_status.get((x,H-1,"Down"), False)))
        # Left edge (excluding corners)
        for y in range(H-2, 0, -1):
            ports.append((f"Port_Thermal_MidLeft{y}", [0,y], "Left", port_status.get((0,y,"Left"), False)))
        return ports



class AddLocationDialog(QDialog):
    def __init__(self, parent, click_pos, layers, W, H):
        super().__init__(parent)
        self.setWindowTitle("Add Location")
        self.click_pos = click_pos
        self.layers = layers
        self.W, self.H = W, H
        self.result = None
        self._build_ui()

    def _build_ui(self):
        form = QFormLayout(self)

        # Type
        self.type_cb = QComboBox()
        self.type_cb.addItems(["Point Marker", "Image Overlay", "Crew"])
        form.addRow("Type:", self.type_cb)

        # Name
        self.name_le = QLineEdit()
        form.addRow("Name:", self.name_le)

        # File picker (image only)
        hb = QHBoxLayout()
        self.file_le = QLineEdit()
        btn_b = QPushButton("Browse…")
        btn_b.clicked.connect(self._browse_file)
        hb.addWidget(self.file_le)
        hb.addWidget(btn_b)
        form.addRow("File:", hb)

        # Size (image only)
        self.w_le = QLineEdit("1")
        self.h_le = QLineEdit("1")
        self.w_le.setPlaceholderText('e.g. 1.5 or 1 32/64')
        self.h_le.setPlaceholderText('e.g. 2.25 or 2 16/64')
        form.addRow("Width (cells):", self.w_le)
        form.addRow("Height (cells):", self.h_le)

        # Layer type (image only)
        self.layer_type_cb = QComboBox()
        self.layer_type_cb.addItems(LAYER_TYPES)
        form.addRow("Layer type:", self.layer_type_cb)

        # Coord mode
        self.coord_cb = QComboBox()
        self.coord_cb.addItems(["Absolute", "Relative"])
        form.addRow("Coord mode:", self.coord_cb)

        # Base layer (if relative)
        self.base_cb = QComboBox()
        self.base_cb.addItems(list(self.layers.keys()))
        form.addRow("Base layer:", self.base_cb)

        # X/Y
        lx = self.click_pos.x()/CELL_SIZE - 1
        ly = self.click_pos.y()/CELL_SIZE - 1
        self.x_le = QLineEdit(f"{lx:.3f}")
        self.y_le = QLineEdit(f"{ly:.3f}")
        form.addRow("X:", self.x_le)
        form.addRow("Y:", self.y_le)

        # Rotation
        self.rot_sb = QDoubleSpinBox()
        self.rot_sb.setRange(-360.0, 360.0)
        self.rot_sb.setSuffix("°")
        form.addRow("Rotation:", self.rot_sb)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self.type_cb.currentIndexChanged.connect(self._update_visibility)
        self.coord_cb.currentIndexChanged.connect(self._update_visibility)
        self._update_visibility()


    def _browse_file(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Select image file", str(Path.home()),
            "Images (*.png *.jpg *.bmp)"
        )
        if f:
            self.file_le.setText(f)


    def _update_visibility(self):
        typ = self.type_cb.currentText()
        is_img = (typ == "Image Overlay")
        is_crew = (typ == "Crew")
        is_rel = (self.coord_cb.currentText() == "Relative")

        self.layer_type_cb.setEnabled(is_img) # Only for images

        # Show/hide file+size controls for image or crew
        for w in (self.file_le, self.w_le, self.h_le):
            w.setVisible(is_img or is_crew)

        # Crew defaults (fixed 1×1, file forced to crew.png)
        if is_crew:
            self.file_le.setText(resource_path("default_images/crew.png"))
            self.file_le.setEnabled(False)
            self.w_le.setText("1")
            self.w_le.setEnabled(False)
            self.h_le.setText("1")
            self.h_le.setEnabled(False)
        else:
            self.file_le.setEnabled(True)
            self.w_le.setEnabled(True)
            self.h_le.setEnabled(True)

        # Keep the "File:" row itself hidden/shown (it’s the parent layout container)
        self.file_le.parentWidget().setVisible(is_img or is_crew)

        # Base target only matters for relative placement
        self.base_cb.setVisible(is_rel)

    def accept(self):
        name = self.name_le.text().strip()
        if not name:
            QMessageBox.warning(self, "Name required", "Please enter a name.")
            return
        typ_sel = self.type_cb.currentText()
        if typ_sel == "Image Overlay":
            typ = "image"
        elif typ_sel == "Crew":
            typ = "crew"
        else:
            typ = "point"
        coord_mode = "rel" if self.coord_cb.currentText() == "Relative" else "abs"
        base = self.base_cb.currentText() if coord_mode == "rel" else None
        x = parse_coord(self.x_le.text())
        y = parse_coord(self.y_le.text())
        rot = self.rot_sb.value()
        res = {
            "type": typ,
            "name": name,
            "coord_mode": coord_mode,
            "base": base,
            "x": x, "y": y,
            "rotation": rot
        }
        if typ == "image":
            file = self.file_le.text().strip()
            if not os.path.isfile(file):
                QMessageBox.warning(self, "File missing", "Select a valid image file.")
                return
            res["file"] = file
            w_val = parse_size(self.w_le.text())
            h_val = parse_size(self.h_le.text())
            if w_val <= 0 or h_val <= 0:
                QMessageBox.warning(self, "Invalid size", "Enter a positive width/height (e.g., 1.5 or 1 32/64).")
                return
            res["w"], res["h"] = w_val, h_val
            # Include the layer type in the result; fall back if UI not added yet
            lt_cb = getattr(self, "layer_type_cb", None)
            res["layer_type"] = lt_cb.currentText() if lt_cb else "floors"
            res["layer_type"] = self.layer_type_cb.currentText()
        elif typ == "crew":
            res["file"] = resource_path("default_images/crew.png")
            res["w"], res["h"] = 1, 1
        self.result = res
        super().accept()

class GridScene(QGraphicsScene):
    def __init__(self, W, H, main_window=None):
        super().__init__(main_window)
        self.W, self.H = W, H
        self.main_window = main_window
        self.cell_states = {}   # (i,j)->{'type','state','rect'}
        self._draw_grid()
        self.blocked_dirs = {}  # (i, j) -> set of blocked directions, e.g. {(1,1): {"Left", "Up"}}

    def _get_blocked_cells(self):
        # Returns dict of (x, y): state for blocked cells
        return {k: v["state"] for k, v in self.cell_states.items() if v["type"] == "blocked"}

    def _draw_grid(self):
        tw, th = (self.W+2)*CELL_SIZE, (self.H+2)*CELL_SIZE
        self.setSceneRect(0,0,tw,th)
        for i in range(self.W+2):
            for j in range(self.H+2):
                rect = QGraphicsRectItem(
                    i*CELL_SIZE, j*CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                rect.setPen(QPen(Qt.black))
                rect.setBrush(QBrush(Qt.white))
                self.addItem(rect)
                coord = f"{i-1},{j-1}"
                txt = QGraphicsTextItem(coord)
                txt.setFont(QFont("Consolas", 10))
                txt.setDefaultTextColor(QColor(0,0,0,160))
                fm = QFontMetricsF(txt.font())
                w, h = fm.horizontalAdvance(coord), fm.height()
                txt.setPos(i*CELL_SIZE + (CELL_SIZE-w)/2,
                           j*CELL_SIZE + (CELL_SIZE-h)/2)
                txt.setZValue(0.1)
                self.addItem(txt)
                is_border = i in (0,self.W+1) or j in (0,self.H+1)
                key = (i-1,j-1)
                if is_border and not ((i in (0,self.W+1)) and (j in (0,self.H+1))):
                    self.cell_states[key] = {
                        "type":"door","state":0,"rect":rect
                    }
                elif not is_border:
                    self.cell_states[key] = {
                        "type":"blocked","state":0,"rect":rect
                    }
    def toggle_cell(self, pos):
        i = int(pos.x()//CELL_SIZE)-1
        j = int(pos.y()//CELL_SIZE)-1
        key = (i,j)
        if key not in self.cell_states:
            return
        c = self.cell_states[key]
        rect = c["rect"]
        if c["type"]=="door":
            c["state"]=(c["state"]+1)%3
            if c["state"]==1: rect.setBrush(QBrush(QColor("lightgreen")))
            elif c["state"]==2: rect.setBrush(QBrush(QColor("lightcoral")))
            else: rect.setBrush(QBrush(Qt.white))
        else:
            c["state"]^=1
            rect.setBrush(QBrush(Qt.gray if c["state"] else Qt.white))
    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        if self.main_window:
            self.main_window._refresh_info_panel()
        if hasattr(self, "click_cb"):
            self.click_cb(ev.scenePos())
        # Blocked Travel Directions arrow click
        if hasattr(self, "mode") and self.mode == "Blocked Travel Directions":
            item = self.itemAt(ev.scenePos(), QTransform())
            if isinstance(item, QGraphicsPixmapItem) and item.data(0):
                x, y, dirn = item.data(0)
                dirs = self.blocked_dirs.setdefault((x, y), set())
                if dirn in dirs:
                    dirs.remove(dirn)
                else:
                    dirs.add(dirn)
                if not dirs:
                    del self.blocked_dirs[(x, y)]
                if self.main_window:
                    self.main_window._refresh_info_panel()
                self.draw_blocked_dir_arrows(self._get_blocked_cells())
    def draw_blocked_dir_arrows(self, blocked_cells):
        # Remove any previous arrows
        if hasattr(self, "_arrow_items"):
            for item in self._arrow_items:
                self.removeItem(item)
        self._arrow_items = []

        W, H = self.W, self.H
        arrow_defs = [
            ("Up",    0, -1, -90),
            ("Down",  0,  1, 90),
            ("Left", -1,  0, 180),
            ("Right", 1,  0, 0),
        ]
        for x in range(W):
            for y in range(H):
                if self.cell_states.get((x, y), {}).get("type") != "blocked":
                    continue
                if blocked_cells.get((x, y), 0) == 1:
                    continue
                for name, dx, dy, deg in arrow_defs:
                    px = (x+1)*CELL_SIZE + CELL_SIZE//2
                    py = (y+1)*CELL_SIZE + CELL_SIZE//2
                    blocked = name in self.blocked_dirs.get((x, y), set())
                    img_path = resource_path("default_images/red_x.png") if blocked else resource_path("default_images/arrow_green.png")
                    pix = QPixmap(img_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item = QGraphicsPixmapItem(pix)
                    item.setOffset(-pix.width()/2, -pix.height()/2)
                    item.setPos(px + dx*22, py + dy*22)  # 22 is a bit further out than 18, tweak as needed
                    item.setRotation(deg)
                    item.setZValue(2)
                    item.setData(0, (x, y, name))
                    self.addItem(item)
                    self._arrow_items.append(item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EasyGridLocations v1.3")
        self.setFont(QFont("Consolas", 10))
        self.last_dir = str(Path.home())
        self.layers = {}   # name -> {'items':[], 'type','params'}
        self._build_ui()
        self.thermal_ports = {}

    def _apply_comment_toggle(self, text: str) -> str:
        """Strip out lines beginning with '//' if toggle is unchecked."""
        if self.include_comments_cb.isChecked():
            return text
        # remove any fully‐commented lines
        return "\n".join(
            line for line in text.splitlines()
            if not line.strip().startswith("//")
        )

    def _apply_indent(self, text: str) -> str:
        indent = "\t" * self.indent_sb.value()
        return "\n".join(
            (indent + line) if line.strip() else ""
            for line in text.splitlines()
        )

    def _build_ui(self):
        c = QWidget(); self.setCentralWidget(c)
        hl = QHBoxLayout(c)
        self.scene = None
        self.view = QGraphicsView()
        self.view.setRenderHints(
            self.view.renderHints()
            | QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
        )
        hl.addWidget(self.view,3)
        ctrl = QVBoxLayout(); hl.addLayout(ctrl,1)
        sh = QHBoxLayout()
        sh.addWidget(QLabel("Part size W,H:"))
        self.size_le=QLineEdit("4,5"); sh.addWidget(self.size_le)
        b=QPushButton("Generate"); b.clicked.connect(self.on_gen); sh.addWidget(b)
        ctrl.addLayout(sh)
        # Load Sprite button: always visible, but disabled until grid is generated
        self.load_sprite_btn = QPushButton("Load Base Image")
        self.load_sprite_btn.setToolTip("Loads the base image and scales it to the Part size.")
        self.load_sprite_btn.setEnabled(False)  # Disabled at start
        self.load_sprite_btn.clicked.connect(self.on_sprite)
        ctrl.addWidget(self.load_sprite_btn)
        mode_hb = QHBoxLayout()
        self.mode_label = QLabel("Mode:")
        mode_hb.addWidget(self.mode_label)
        self.mode_cb = QComboBox()
        self.mode_cb.addItems([
            "Doors & Paths",
            "Blocked Travel Directions",  # <-- Add this
            "Locations",
            "Thermal Ports"
        ])
        mode_hb.addWidget(self.mode_cb)
        ctrl.addLayout(mode_hb)
        self.mode_cb.currentIndexChanged.connect(self._mode_changed)
        self.mode_cb.setEnabled(False)
        self.global_coord_label = QLabel("Global coord mode:")
        self.global_coord_cb = QComboBox()
        self.global_coord_cb.addItems(["Direct", "Offset"])
        ctrl.addWidget(self.global_coord_label)
        ctrl.addWidget(self.global_coord_cb)
        self.global_coord_label.hide()
        self.global_coord_cb.hide()
        # ---- Start: Code Viewer ----
        self.code_viewer_label = QLabel("Code Viewer")
        self.code_viewer_label.setStyleSheet("font-weight: bold;")
        ctrl.addWidget(self.code_viewer_label)
        self.info_panel = QPlainTextEdit()
        self.info_panel.setReadOnly(True)
        ctrl.addWidget(self.info_panel)
        # ---- End: Code Viewer ----

        # --- Layers & Points section ---
        self.layers_label = QLabel("Layers & Points:")
        ctrl.addWidget(self.layers_label)
        self.layers_label.hide()  # Start hidden

        self.tree = QTreeWidget(); self.tree.setHeaderHidden(True)
        self.tree.itemChanged.connect(self._on_tree_item_changed)
        self.tree.itemSelectionChanged.connect(self._on_tree_sel)
        ctrl.addWidget(self.tree, 1)
        self.tree.hide()  # Start hidden

        # Allows Drag & Drop reordering of items
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree.model().rowsMoved.connect(lambda *args: self._rebuild_z_order())

        self.props_label = QLabel("Properties:")
        ctrl.addWidget(self.props_label)
        self.props_label.hide()  # Start hidden

        self.props_box = QGroupBox(); self.props_layout = QFormLayout()
        self.props_box.setLayout(self.props_layout)
        ctrl.addWidget(self.props_box)
        self.props_box.hide()  # Already hiding

        # --- Copy Code Block button: move here, after tree, before Copy/Save ---
        self.copy_block_btn = QPushButton("Copy Code Block")
        self.copy_block_btn.clicked.connect(self._context_copy)
        ctrl.addWidget(self.copy_block_btn)
        self.copy_block_btn.hide()  # Hide at startup, control visibility in _mode_changed

        # — Copy / Save / Include‑Comments toggle —
        cb = QPushButton("Copy All")
        cb.clicked.connect(self.on_copy)
        ctrl.addWidget(cb)

        sv = QPushButton("Save All")
        sv.clicked.connect(self.on_save)
        ctrl.addWidget(sv)

        # ─── Include Comments checkbox ──────────────────────────────────────────
        # This checkbox allows toggling whether to include commented‐out lines in any copy/save    
        from PySide6.QtWidgets import QCheckBox
        self.include_comments_cb = QCheckBox("Include comments")
        self.include_comments_cb.setChecked(True)
        ctrl.addWidget(self.include_comments_cb)
        # ─── End Include Comments checkbox ──────────────────────────────────────
        
        # ─── Indent levels ────────────────────────────────────────────────────────
        indent_hb = QHBoxLayout()
        indent_hb.addWidget(QLabel("Indent levels:"))
        self.indent_sb = QSpinBox()
        self.indent_sb.setRange(0, 10)    # allow 0–10 tabs
        self.indent_sb.setValue(2)        # default to 2
        indent_hb.addWidget(self.indent_sb)
        ctrl.addLayout(indent_hb)
        # ─── End Indent levels ────────────────────────────────────────────────────

        # Status bar
        self.statusBar().showMessage("Ready")
        self._mode_changed()

    def _mode_changed(self):
        if self.scene is None:
            # Grid not yet created, do nothing
            return
        mode = self.mode_cb.currentText()

        # Hide global coord mode always
        self.global_coord_label.hide()
        self.global_coord_cb.hide()

        if mode == "Locations":
            self.code_viewer_label.hide()
            self.info_panel.hide()
            self.copy_block_btn.show()
            self.layers_label.show()
            self.tree.show()
            self.props_label.show()
            self.props_box.show()
        else:  # Doors & Paths or Thermal Ports
            self.code_viewer_label.show()
            self.info_panel.show()
            self.copy_block_btn.show()
            self.layers_label.hide()
            self.tree.hide()
            self.props_label.hide()
            self.props_box.hide()
            self._refresh_info_panel()
        if mode == "Blocked Travel Directions":
            self.scene.mode = "Blocked Travel Directions"
            self.scene.draw_blocked_dir_arrows(self.scene._get_blocked_cells())
        else:
            if hasattr(self.scene, "_arrow_items"):
                for item in self.scene._arrow_items:
                    self.scene.removeItem(item)
                self.scene._arrow_items = []
    
        self.copy_block_btn.show()  # Always show

        # Visual logic for port items
        if mode == "Thermal Ports":
            self._draw_thermal_ports()
            self._refresh_info_panel()
        else:
            if hasattr(self, "_port_items"):
                for item in self._port_items:
                    self.scene.removeItem(item)
                self._port_items = []

    def _gen_blocked_travel_dirs_code(self):
        if not self.scene:
            return ""
        W, H = self.scene.W, self.scene.H
        blocked_dirs = getattr(self.scene, "blocked_dirs", {})
        entries = []
        for (i, j), dirs in blocked_dirs.items():
            if dirs:
                entries.append((i, j, sorted(dirs)))
        if not entries:
            out = ["// BlockedTravelCellDirections", "// ["]
            for y in range(H):
                for x in range(W):
                    for d in ["Up", "Down", "Left", "Right"]:
                        out.append(f"//{INDENT}{{")
                        out.append(f"//{INDENT}{INDENT}Key = [{x}, {y}]")
                        out.append(f"//{INDENT}{INDENT}Value = [{d}]")
                        out.append(f"//{INDENT}}}")
            out.append("// ]")
            return "\n".join(out)
        else:
            out = ["BlockedTravelCellDirections", "["]
            for (i, j, dirs) in entries:
                out.append(f"{INDENT}{{")
                out.append(f"{INDENT}{INDENT}Key = [{i}, {j}]")
                out.append(f"{INDENT}{INDENT}Value = [{', '.join(dirs)}]")
                out.append(f"{INDENT}}}")
            out.append("]")
            return "\n".join(out)

    def _context_copy(self):
        mode = self.mode_cb.currentText()
        if mode == "Locations":
            txt = self._gen_locations_code()
            # no comment toggle here, just indent
            txt = self._apply_indent(txt)
        else:
            raw = self.info_panel.toPlainText()
            txt = self._apply_comment_toggle(raw)
            txt = self._apply_indent(txt)
        QApplication.clipboard().setText(txt)
        self.statusBar().showMessage("Copied code block")

    def _draw_thermal_ports(self):
        if hasattr(self, "_port_items"):
            try:
                for item in self._port_items:
                    if item.scene() is not None:
                        self.scene.removeItem(item)
            except RuntimeError:
                pass
        self._port_items = []
        W, H = self.scene.W, self.scene.H
        for i in range(W):
            for j in [-1, H]:
                self.thermal_ports.setdefault((i,j), False)
        for j in range(H):
            for i in [-1, W]:
                self.thermal_ports.setdefault((i,j), False)
        for (i, j), enabled in self.thermal_ports.items():
            px = (i+1)*CELL_SIZE + CELL_SIZE//2
            py = (j+1)*CELL_SIZE + CELL_SIZE//2
            char = None
            if j == -1 and 0 <= i < W:
                char = '^'
            elif j == H and 0 <= i < W:
                char = 'v'
            elif i == -1 and 0 <= j < H:
                char = '<'
            elif i == W and 0 <= j < H:
                char = '>'
            if char and enabled:
                arrow = QGraphicsTextItem(char)
                arrow.setFont(QFont("Consolas", 24, QFont.Bold))
                arrow.setDefaultTextColor(QColor("#FF8800"))
                arrow.setPos(px-8, py-14)
                arrow.setZValue(1.5)
                self.scene.addItem(arrow)
                self._port_items.append(arrow)
            elif char:
                size = 14
                x1, y1 = px - size//2, py - size//2
                x2, y2 = px + size//2, py + size//2
                line1 = QGraphicsLineItem(x1, y1, x2, y2)
                line2 = QGraphicsLineItem(x1, y2, x2, y1)
                pen = QPen(QColor("gray"), 3)
                for ln in (line1, line2):
                    ln.setPen(pen)
                    ln.setZValue(1.2)
                    self.scene.addItem(ln)
                    self._port_items.append(ln)

    def on_gen(self):
        txt=self.size_le.text()
        try:
            w,h=map(int,txt.split(","))
            assert 1<=w<=MAX_INTERIOR
        except:
            QMessageBox.warning(self,"Bad size","Enter W,H between 1 and "+str(MAX_INTERIOR))
            return
        self.layers.clear(); self.tree.clear()
        self.thermal_ports = {}
        for i in range(w):
            self.thermal_ports[(i,-1)] = False
            self.thermal_ports[(i,h)] = False
        for j in range(h):
            self.thermal_ports[(-1,j)] = False
            self.thermal_ports[(w,j)] = False
        self._port_items = []
        self.scene=GridScene(w,h)
        self.scene = GridScene(w, h, main_window=self)
        self.scene.mode = self.mode_cb.currentText()
        self.scene.click_cb=self._on_click
        self.view.setScene(self.scene)
        self.view.resetTransform(); self.view.translate(-CELL_SIZE,-CELL_SIZE)
        self.load_sprite_btn.setEnabled(True)
        self.mode_cb.setEnabled(True)
        self.statusBar().showMessage(f"Grid {w}×{h}")
        self._mode_changed()    # <<<<<< Add this, removes the need to call _refresh_info_panel() here
        # self._refresh_info_panel()

    def on_sprite(self):
        if not self.scene:
            return
        # pick file
        f, _ = QFileDialog.getOpenFileName(
            self, "Load Base Image", self.last_dir, "Images (*.png *.jpg *.bmp)"
        )
        if not f:
            return
        self.last_dir = os.path.dirname(f)

        # scale to the Part (inner grid) size
        W, H = self.scene.W, self.scene.H
        width_px  = int(round(W * CELL_SIZE))
        height_px = int(round(H * CELL_SIZE))
        pix = QPixmap(f).scaled(
            width_px, height_px,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )

        # create & center over the INNER grid (offset by the 1-cell border)
        img = QGraphicsPixmapItem(pix)
        img.setOpacity(0.7)
        img.setZValue(0.5)  # above grid (0/0.1), below all overlays
        ox = CELL_SIZE + (W * CELL_SIZE - pix.width())  / 2
        oy = CELL_SIZE + (H * CELL_SIZE - pix.height()) / 2
        img.setPos(ox, oy)
        img.setTransformOriginPoint(pix.width() / 2, pix.height() / 2)
        img.setRotation(0)

        self.scene.addItem(img)
        # keep the little red arrow, centered
        arrow = self._make_arrow(ox + pix.width() / 2, oy + pix.height() / 2, 0)
        self.scene.addItem(arrow)

        # register layer (special key), auto size = part size
        name = "__sprite__"
        self.layers[name] = {
            "items": [img, arrow],
            "type": "image",
            "params": {
                "file": f,
                "size": (W, H),
                "location": (0, 0),
                "rotation": 0.0,
            },
        }

        # show as "Base Image" in the tree
        node = QTreeWidgetItem(self.tree, ["Base Image"])
        node.setData(0, Qt.UserRole, name)
        node.setCheckState(0, Qt.Checked)
        self.tree.setCurrentItem(node)

        # restack after adding
        self._rebuild_z_order()



    def _make_arrow(self,x,y,deg):
        rad = math.radians(deg - 90)
        ex = x + ARROW_LEN * math.cos(rad)
        ey = y + ARROW_LEN * math.sin(rad)
        ln = QGraphicsLineItem(x, y, ex, ey)
        pen = QPen(QColor("red"), 2)
        ln.setPen(pen)
        ln.setZValue(1)
        return ln

    def _make_arrow_colored(self, x, y, deg, color="#FF8800"):
        rad = math.radians(deg - 90)
        ex = x + ARROW_LEN * math.cos(rad)
        ey = y + ARROW_LEN * math.sin(rad)
        ln = QGraphicsLineItem(x, y, ex, ey)
        pen = QPen(QColor(color), 2)
        ln.setPen(pen)
        ln.setZValue(1.3)
        return ln

    def _on_click(self, pos):
        mode = self.mode_cb.currentText()
        if mode == "Doors & Paths":
            self.scene.toggle_cell(pos)
        elif mode == "Locations":
            dlg=AddLocationDialog(self,pos,self.layers,self.scene.W,self.scene.H)
            if dlg.exec()!=QDialog.Accepted: return
            self._add_location(dlg.result)
        elif mode == "Thermal Ports":
            i = int(pos.x() // CELL_SIZE) - 1
            j = int(pos.y() // CELL_SIZE) - 1
            W, H = self.scene.W, self.scene.H
            is_perimeter = (
                (0 <= i < W and (j == -1 or j == H)) or
                (0 <= j < H and (i == -1 or i == W))
            )
            if not is_perimeter:
                return
            key = (i, j)
            enabled = self.thermal_ports.get(key, False)
            self.thermal_ports[key] = not enabled
            self._draw_thermal_ports()
        # === Always refresh the info panel after a click ===
        self._refresh_info_panel()

    def _add_location(self, opts):
        x, y = opts["x"], opts["y"]
        if opts["coord_mode"] == "rel":
            base = opts["base"]
            bx, by = self.layers[base]["params"]["location"]
            x, y = bx + x, by + y

        px, py = (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
        rot = opts["rotation"]
        name = opts["name"]

        if opts["type"] == "point":
            # ----- POINT (no file/size/layer_type) -----
            dot = QGraphicsEllipseItem(px - 5, py - 5, 10, 10)
            dot.setBrush(QBrush(Qt.red))
            dot.setZValue(9999)  # points on top in editor
            dot.setTransformOriginPoint(px, py)
            dot.setRotation(rot)
            arr = self._make_arrow(px, py, rot)
            self.scene.addItem(dot)
            self.scene.addItem(arr)
            self.layers[name] = {
                "items": [dot, arr], "type": "point",
                "params": {
                    "location": (x, y),
                    "rotation": rot
                }
            }

        elif opts["type"] == "crew":
            # ----- CREW (fixed 1x1, no explicit layer_type in code export) -----
            f = resource_path("default_images/crew.png")
            w, h = 1, 1
            pix = QPixmap(f).scaled(
                int(round(w * CELL_SIZE)), int(round(h * CELL_SIZE)),
                Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
            img = QGraphicsPixmapItem(pix)
            img.setOpacity(0.7)
            img.setZValue(0.5)
            img.setTransformOriginPoint(pix.width() / 2, pix.height() / 2)
            img.setRotation(rot)
            img.setPos(px - pix.width() / 2, py - pix.height() / 2)
            arr = self._make_arrow(px, py, rot)
            self.scene.addItem(img)
            self.scene.addItem(arr)
            self.layers[name] = {
                "items": [img, arr], "type": "crew",
                "params": {
                    "file": "default_images/crew.png",
                    "size": (1, 1),
                    "location": (x, y),
                    "rotation": rot
                }
            }

        else:
            # ----- IMAGE OVERLAY (file/size + layer_type) -----
            f = opts["file"]
            w, h = opts["w"], opts["h"]
            pix = QPixmap(f).scaled(
                int(round(w * CELL_SIZE)), int(round(h * CELL_SIZE)),
                Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
            img = QGraphicsPixmapItem(pix)
            img.setOpacity(0.7)
            img.setZValue(0.5)
            img.setTransformOriginPoint(pix.width() / 2, pix.height() / 2)
            img.setRotation(rot)
            img.setPos(px - pix.width() / 2, py - pix.height() / 2)
            arr = self._make_arrow(px, py, rot)
            self.scene.addItem(img)
            self.scene.addItem(arr)
            self.layers[name] = {
                "items": [img, arr], "type": "image",
                "params": {
                    "file": f,
                    "size": (w, h),
                    "location": (x, y),
                    "rotation": rot,
                    "layer_type": opts.get("layer_type", "floors")
                }
            }

        node = QTreeWidgetItem(self.tree, [name])
        node.setData(0, Qt.UserRole, name)
        node.setCheckState(0, Qt.Checked)
        node.setFlags(node.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.tree.setCurrentItem(node)
        self._rebuild_z_order()
        self.statusBar().showMessage(f"Added {name}")
        self._refresh_info_panel()

    
    def _on_tree_sel(self):
        items = self.tree.selectedItems()
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not items:
            self.props_box.hide()
            return

        key = items[0].data(0, Qt.UserRole)
        L = self.layers[key]
        p = L["params"]
        self.props_box.show()

        self.p_name = QLineEdit(key)
        self.props_layout.addRow("Name:", self.p_name)

        self.p_x = QLineEdit(str(p["location"][0]))
        self.p_y = QLineEdit(str(p["location"][1]))
        self.props_layout.addRow("X:", self.p_x)
        self.props_layout.addRow("Y:", self.p_y)

        self.p_rot = QDoubleSpinBox()
        self.p_rot.setRange(-360.0, 360.0)
        self.p_rot.setValue(p["rotation"])
        self.p_rot.setSuffix("°")
        self.props_layout.addRow("Rotation:", self.p_rot)

        # Layer Type (images only)
        if L["type"] == "image":
            # assumes LAYER_TYPES is defined globally
            self.p_layer_type = QComboBox()
            self.p_layer_type.addItems(LAYER_TYPES if 'LAYER_TYPES' in globals() else [
                "floors","walls","doodads_low","doodads_high","weapons","doors"
            ])
            self.p_layer_type.setCurrentText(p.get("layer_type", "floors"))
            self.props_layout.addRow("Layer type:", self.p_layer_type)

        btn_remove = QPushButton("Remove Layer")
        btn_remove.clicked.connect(lambda: self._remove_layer(key))
        self.props_layout.addRow(btn_remove)

        btn_apply = QPushButton("Apply Changes")
        btn_apply.clicked.connect(lambda: self._apply_props(key))
        self.props_layout.addRow(btn_apply)

        # Move layer in the list (affects Z stacking)
        btn_up = QPushButton("Move Up")
        btn_down = QPushButton("Move Down")
        btn_up.clicked.connect(lambda: self._move_layer(key, -1))
        btn_down.clicked.connect(lambda: self._move_layer(key, +1))
        self.props_layout.addRow(btn_up, btn_down)

    def _apply_props(self, key):
        L = self.layers[key]
        items = L["items"]
        p = L["params"]

        # location & rotation
        x = parse_coord(self.p_x.text())
        y = parse_coord(self.p_y.text())
        rot = self.p_rot.value()
        p["location"] = (x, y)
        p["rotation"] = rot

        px, py = (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE

        if L["type"] == "point":
            # update point
            dot, arr = items
            dot.setRect(px - 5, py - 5, 10, 10)
            dot.setTransformOriginPoint(px, py)
            dot.setRotation(rot)
            self.scene.removeItem(arr)
            new_arr = self._make_arrow(px, py, rot)
            self.scene.addItem(new_arr)
            items[1] = new_arr

        else:
            # image or crew
            img, arr = items

            # capture layer type from properties (images only)
            if L["type"] == "image" and hasattr(self, "p_layer_type"):
                p["layer_type"] = self.p_layer_type.currentText()

            # handle size & pixmap
            if L["type"] == "image":
                new_w = parse_size(self.p_w.text()) if hasattr(self, "p_w") else p["size"][0]
                new_h = parse_size(self.p_h.text()) if hasattr(self, "p_h") else p["size"][1]
                if new_w <= 0 or new_h <= 0:
                    QMessageBox.warning(self, "Invalid size", "Width/Height must be > 0.")
                    return
                p["size"] = (new_w, new_h)
                f = p["file"]
                new_pix = QPixmap(f).scaled(
                    int(round(new_w * CELL_SIZE)),
                    int(round(new_h * CELL_SIZE)),
                    Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                )
                img.setPixmap(new_pix)
                pw, ph = new_pix.width(), new_pix.height()
            else:
                # crew: keep current pixmap size
                pw, ph = img.pixmap().width(), img.pixmap().height()

            # re-center origin & apply rotation/position
            img.setTransformOriginPoint(pw / 2, ph / 2)
            img.setRotation(rot)
            img.setPos(px - pw / 2, py - ph / 2)

            # rebuild the arrow
            self.scene.removeItem(arr)
            new_arr = self._make_arrow(px, py, rot)
            self.scene.addItem(new_arr)
            items[1] = new_arr

        # restack & refresh
        self._rebuild_z_order()
        self.statusBar().showMessage(f"Updated {key}")
        self._refresh_info_panel()


    def _remove_layer(self,key):
        for item in self.layers[key]["items"]:
            self.scene.removeItem(item)
        del self.layers[key]
        iters = self.tree.findItems(key, Qt.MatchExactly|Qt.MatchRecursive)
        for it in iters:
            parent = it.parent() or self.tree.invisibleRootItem()
            parent.removeChild(it)
        self.props_box.hide()
        self.statusBar().showMessage(f"Removed {key}")
        self._refresh_info_panel()

    def _on_tree_item_changed(self, item, col):
        key = item.data(0, Qt.UserRole)
        if not key:
            return
        L = self.layers.get(key)
        if not L:
            return
        visible = (item.checkState(0) == Qt.Checked)
        for g in L["items"]:
            g.setVisible(visible)

    def _move_layer(self, key, delta):
        # keep __sprite__ pinned at the bottom
        if key == "__sprite__":
            return
        parent = self.tree.invisibleRootItem()
        item = self.tree.currentItem()
        if not item:
            return
        idx = parent.indexOfChild(item)
        new_idx = max(0, min(parent.childCount() - 1, idx + delta))
        if new_idx == idx:
            return
        take = parent.takeChild(idx)
        parent.insertChild(new_idx, take)
        self.tree.setCurrentItem(take)
        self._rebuild_z_order()

    def _rebuild_z_order(self):
        """
        Editor Z rules:
            - Base Image (__sprite__) sits at 0.5 (above grid 0/0.1, below overlays)
            - Image overlays ordered by LAYER_Z rank (lowest bucket under highest),
            but mapped to editor-friendly bands: 1.0 + rank*10
            - Within the same layer_type, keep current tree order via tiny offsets
            - Crew sits between 'doors' and 'weapons' bands
            - Points always on top
        """
        root = self.tree.invisibleRootItem()

        # 1) Base image above grid, below overlays
        if "__sprite__" in self.layers:
            for g in self.layers["__sprite__"]["items"]:
                g.setZValue(0.5)

        # 2) Determine ranks from LAYER_Z (fall back to default map if missing)
        try:
            layer_z_map = LAYER_Z
        except NameError:
            layer_z_map = {
                "structure_construction": -750, "floors": -700, "turrets": -600,
                "doodads_low": -500, "walls_stencil": -400, "external_walls": -300,
                "walls": -200, "doors": -100, "weapons": 0, "doodads_high": 100,
                "lights_add": 200, "fire": 300, "roofs": 1000, "roof_doodads": 1100,
                "construction": 1150, "construction_delta": 1175, "roof_turrets": 1200,
                "roof_lights_fancy": 1300,
            }

        # sort by bucket (low → high) and rank them
        sorted_types = [t for t, _ in sorted(layer_z_map.items(), key=lambda kv: kv[1])]
        rank = {t: i for i, t in enumerate(sorted_types)}

        band = 10.0
        base_offset = 1.0  # all overlays start above sprite/grid
        # crew midway between 'doors' and 'weapons'
        r_doors = rank.get("doors", 0)
        r_weapons = rank.get("weapons", r_doors + 1)
        crew_base = base_offset + ((r_doors + r_weapons) / 2.0) * band
        points_z = 9999.0

        # 3) Collect keys in current tree order
        grouped = {}    # layer_type -> [keys...]
        crew_keys = []
        point_keys = []
        other_keys = []

        for i in range(root.childCount()):
            it = root.child(i)
            key = it.data(0, Qt.UserRole)
            if not key or key == "__sprite__":
                continue
            L = self.layers.get(key)
            if not L:
                continue
            if L["type"] == "image":
                lt = L["params"].get("layer_type", "floors")
                grouped.setdefault(lt, []).append(key)
            elif L["type"] == "crew":
                crew_keys.append(key)
            elif L["type"] == "point":
                point_keys.append(key)
            else:
                other_keys.append(key)

        # 4) Apply Z for image layers: 1.0 + rank*10 (+ tiny offsets)
        for lt, keys in grouped.items():
            r = rank.get(lt, 0)
            base = base_offset + r * band
            for idx, key in enumerate(keys):
                z = base + idx * 0.01
                its = self.layers[key]["items"]
                its[0].setZValue(z)
                if len(its) > 1:
                    its[1].setZValue(z + 0.001)

        # 5) Crew between doors & weapons
        for idx, key in enumerate(crew_keys):
            z = crew_base + idx * 0.01
            its = self.layers[key]["items"]
            its[0].setZValue(z)
            if len(its) > 1:
                its[1].setZValue(z + 0.001)

        # 6) Points always on top (editor-only)
        for idx, key in enumerate(point_keys):
            z = points_z + idx * 0.01
            its = self.layers[key]["items"]
            its[0].setZValue(z)
            if len(its) > 1:
                its[1].setZValue(z + 0.001)

        # 7) Fallback any odd types to the topmost band
        top_band = base_offset + (len(sorted_types) + 1) * band
        for idx, key in enumerate(other_keys):
            its = self.layers[key]["items"]
            z = top_band + idx * 0.01
            its[0].setZValue(z)
            if len(its) > 1:
                its[1].setZValue(z + 0.001)


    def on_copy(self):
        raw = self._gen_rules()
        txt = self._apply_comment_toggle(raw)
        txt = self._apply_indent(txt)
        QApplication.clipboard().setText(txt)
        self.statusBar().showMessage("Copied")

    def on_save(self):
        raw = self._gen_rules()
        txt = self._apply_comment_toggle(raw)
        txt = self._apply_indent(txt)

        # allow .rules or .txt
        path, fmt = QFileDialog.getSaveFileName(
            self, "Save output", self.last_dir,
            "Rules (*.rules);;Text Files (*.txt)"
        )
        if not path:
            return

        # enforce extension
        ext = ".rules" if fmt == "Rules (*.rules)" else ".txt"
        if not path.lower().endswith(ext):
            path += ext

        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)

        self.last_dir = os.path.dirname(path)
        self.statusBar().showMessage(f"Saved {path}")

    def _gen_rules(self):
        W, H = self.scene.W, self.scene.H
        lines = [f"size = [{W}, {H}]\n"]

        # AllowedDoorLocations & BlockedTravelCells (reuse mode-specific generator for consistency)
        doors_and_paths = self._gen_doors_paths_code()
        lines.append(doors_and_paths)
        lines.append("")

        # BlockedTravelCellDirections
        blocked_dirs = self._gen_blocked_travel_dirs_code()
        if blocked_dirs.strip():
            lines.append(blocked_dirs)
            lines.append("")

        # Thermal Ports
        thermal_ports = self._gen_thermal_ports_code()
        if thermal_ports.strip():
            lines.append(thermal_ports)
            lines.append("")

        # Locations
        lines.append(self._gen_locations_code())

        return "\n".join(lines)

    # === Code Viewer Updater ===
    def _refresh_info_panel(self):
        if not self.scene:
            self.info_panel.clear()
            return
        mode = self.mode_cb.currentText()
        if mode == "Doors & Paths":
            code = self._gen_doors_paths_code()
            self.info_panel.setPlainText(code)
        elif mode == "Blocked Travel Directions":
            self.scene.draw_blocked_dir_arrows(self.scene._get_blocked_cells())
            code = self._gen_blocked_travel_dirs_code()
            self.info_panel.setPlainText(code)
        elif mode == "Thermal Ports":
            code = self._gen_thermal_ports_code()
            self.info_panel.setPlainText(code)
        else:
            self.info_panel.clear()

    # === Doors & Paths Code Generator ===
    def _gen_doors_paths_code(self):
        if not self.scene:
            return ""
        W, H = self.scene.W, self.scene.H
        doors = []
        for x in range(W):
            doors.append((x, -1))
            doors.append((x, H))
        for y in range(H):
            doors.append((-1, y))
            doors.append((W, y))
        cell_states = getattr(self.scene, 'cell_states', {})

        # Gather states
        has_green = False
        has_red = False
        for (i, j) in doors:
            state = cell_states.get((i, j), {})
            if state.get("type") == "door":
                if state.get("state", 0) == 1:
                    has_green = True
                elif state.get("state", 0) == 2:
                    has_red = True

        all_neutral = not (has_green or has_red)

        out = []
        if all_neutral:
            # All neutral: comment out the whole block
            out.append("// AllowedDoorLocations")
            out.append("// [")
            for (i, j) in doors:
                out.append(f"//\t[{i}, {j}]")
            out.append("// ]\n")
        else:
            out.append("AllowedDoorLocations")
            out.append("[")
            for (i, j) in doors:
                state = cell_states.get((i, j), {})
                if state.get("type") == "door":
                    s = state.get("state", 0)
                    if has_green and has_red:
                        # Both green and red: neutral are assumed blocked (commented), green uncommented, red commented
                        if s == 1:
                            out.append(f"\t[{i}, {j}]")
                        elif s == 2 or s == 0:
                            out.append(f"\t// [{i}, {j}]")
                    elif has_green and not has_red:
                        # Only green: green uncommented, neutral commented
                        if s == 1:
                            out.append(f"\t[{i}, {j}]")
                        else:
                            out.append(f"\t// [{i}, {j}]")
                    elif has_red and not has_green:
                        # Only red: red commented, neutral uncommented
                        if s == 2:
                            out.append(f"\t// [{i}, {j}]")
                        else:
                            out.append(f"\t[{i}, {j}]")
                else:
                    out.append(f"\t// [{i}, {j}]")
            out.append("]\n")

        # BlockedTravelCells: only care about "blocked" type
        blocked = []
        for y in range(H):
            for x in range(W):
                blocked.append((x, y))

        block_lines = []
        any_blocked = False
        for (i, j) in blocked:
            state = cell_states.get((i, j), {})
            if state.get("type") == "blocked":
                if state.get("state", 0) == 1:
                    block_lines.append(f"\t[{i}, {j}]")
                    any_blocked = True
                else:
                    block_lines.append(f"\t// [{i}, {j}]")
            else:
                block_lines.append(f"\t// [{i}, {j}]")

        block_block_commented = not any(line.lstrip().startswith("[") for line in block_lines)
        if block_block_commented:
            out += ["// BlockedTravelCells", "// ["]
            out += [f"//{line}" for line in block_lines]
            out.append("// ]")
        else:
            out += ["BlockedTravelCells", "["]
            out += block_lines
            out.append("]")

        return "\n".join(out)

    # === Locations Code Generator ===
    def _gen_locations_code(self):
        lines = []
        for name, L in self.layers.items():
            if name == "__sprite__":
                continue
            p = L["params"]
            lines.append(f"{name}")
            lines.append("{")
            if L["type"] == "image":
                lines.append(f'{INDENT}File = "{p["file"]}"')
                lines.append(f"{INDENT}Size = [{p['size'][0]}, {p['size'][1]}]")
                lines.append(f"{INDENT}Location = [{p['location'][0]}, {p['location'][1]}]")
                lines.append(f"{INDENT}Rotation = {p['rotation']}")
            elif L["type"] == "crew":
                lines.append(f'{INDENT}Type = CrewLocation')
                lines.append(f"{INDENT}Location = [{p['location'][0]}, {p['location'][1]}]")
                lines.append(f"{INDENT}Rotation = {p['rotation']}d")
            elif L["type"] == "point":
                lines.append(f"{INDENT}Location = [{p['location'][0]}, {p['location'][1]}]")
                lines.append(f"{INDENT}Rotation = {p['rotation']}")
            lines.append("}")
            lines.append("")
        return "\n".join(lines)

    # === Thermal Ports Code Generator ===
    def _gen_thermal_ports_code(self):
        W, H = self.scene.W, self.scene.H
        lines = []
        port_status = {}
        for i in range(W):
            port_status[(i,0,"Up")] = self.thermal_ports.get((i,-1), False)
            port_status[(i,H-1,"Down")] = self.thermal_ports.get((i,H), False)
        for j in range(H):
            port_status[(0,j,"Left")] = self.thermal_ports.get((-1,j), False)
            port_status[(W-1,j,"Right")] = self.thermal_ports.get((W,j), False)
        ports = vanilla_ports_all(W, H, port_status)
        # Output all ports in order, commented out if disabled
        if ports:
            lines.append("// --- Thermal Ports ---\n")
            enabled_indices = [i for i, (_, _, _, en) in enumerate(ports) if en]
            if enabled_indices:
                prev_enabled_name = None
                last_enabled_for_loc = {}  # (x, y) -> (name, dirn, enabled)
                last_enabled_for_dir = {}  # dirn -> (name, loc, enabled)
                for idx, (name, loc, dirn, enabled) in enumerate(ports):
                    loc_tuple = tuple(loc)
                    # Determine inheritance base
                    if prev_enabled_name is None:
                        base = "~/Part/^/0/BASE_THERMAL_PORT"
                    else:
                        base = prev_enabled_name

                    parent_for_loc = last_enabled_for_loc.get(loc_tuple, None)
                    parent_for_dir = last_enabled_for_dir.get(dirn, None)

                    # Figure out what the parent (base) port's location and direction are
                    parent_loc = None
                    parent_dir = None
                    if prev_enabled_name is not None:
                        # Find previous enabled port's loc/dir
                        prev_idx = idx - 1
                        while prev_idx >= 0:
                            prev_port = ports[prev_idx]
                            if prev_port[3]:  # enabled
                                parent_loc = tuple(prev_port[1])
                                parent_dir = prev_port[2]
                                break
                            prev_idx -= 1

                    # Decide what to output
                    needs_loc = (parent_loc != loc_tuple) if parent_loc is not None else True
                    needs_dir = (parent_dir != dirn) if parent_dir is not None else True

                    if enabled:
                        block = [f"{name} : {base}", "{"]
                        if needs_loc:
                            block.append(f"{INDENT}Location = [{loc[0]}, {loc[1]}]")
                        if needs_dir:
                            block.append(f"{INDENT}Direction = {dirn}")
                        block.append("}")
                        lines += block
                        lines.append("")
                        prev_enabled_name = name
                        last_enabled_for_loc[loc_tuple] = (name, dirn, True)
                        last_enabled_for_dir[dirn] = (name, loc_tuple, True)
                    else:
                        block = [f"// {name} : {base}", "// {"]
                        if needs_loc:
                            block.append(f"//{INDENT}Location = [{loc[0]}, {loc[1]}]")
                        if needs_dir:
                            block.append(f"//{INDENT}Direction = {dirn}")
                        block.append("// }")
                        lines += block
                        lines.append("")
                        last_enabled_for_loc[loc_tuple] = (name, dirn, False)
                        last_enabled_for_dir[dirn] = (name, loc_tuple, False)
            else:
                # All ports disabled—comment all as inheriting from BASE_THERMAL_PORT
                for idx, (name, loc, dirn, enabled) in enumerate(ports):
                    block = [
                        f"// {name} : ~/Part/^/0/BASE_THERMAL_PORT",
                        "// {",
                        f"//{INDENT}Location = [{loc[0]}, {loc[1]}]",
                        f"//{INDENT}Direction = {dirn}",
                        "// }"
                    ]
                    lines += block
                    lines.append("")

        return "\n".join(lines)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the splash screen if the file exists
    splash_img = resource_path("default_images/easygrid_splash.png")
    splash = None
    if os.path.exists(splash_img):
        splash_pix = QPixmap(splash_img)
        splash = QSplashScreen(splash_pix)
        splash.show()
        QGuiApplication.processEvents()

    QThread.msleep(5000)  # <-- Show splash for N seconds (N*1000 ms)

    win = MainWindow()
    win.resize(1200, 800)
    win.show()

    if splash:
        splash.finish(win)  

    sys.exit(app.exec())
