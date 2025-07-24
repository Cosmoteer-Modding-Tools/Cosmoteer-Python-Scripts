
# TODO
# Locations Mode should include a "Crew" option in the AddLocation popup dialog under "Type" menu, it should default the image of a crew member for easier placement (default_images/crew.png).  For convenince it should ensure the size is 1x1 and image orientation iss the same default as adding images manually. When selected it should be at 100% opacity and toggleable in the layer menu (all same features of adding points and images - basically a combination of both allowing the direction arrow to overlay so the user can be precise in its rotation - also adjustable and applyed in properties when highlighted in teh layer menu like the other features.).
# When outputting Thermal Port code, physical location values don't need to be specified if they are inheriting from a node sharing the same location. This will need to be careful not to break when you toggle off the the inherited value for any reason, it should work similar to the Base Inherit and show up on one of the remaining nodes that previously shared the location.  E.g., Port A and B and C have same location = [0,0], Port C inherits B and B inherits A but each has its own distinct directional value (up left and right).  Port C and B don't need to have a location unless Port A is disabled, if Port A is disabled, then Port B should have its location uncommented, so C can inherit from it (or vice versa).  I think for an easier implementation we should just comment and uncomment out values rather than removing them.  That way we don't have to worry about losing or regenerating code.  
# Allowed Door locations and Travel Cells code blocks should use the following format - There is a bug currently where the default code block is not being commented out like it should be.  If Neutral (not green or red) the AllowedDoorLocations should be commented out.  If a door is dissallowed (red) and all other perimeter blocks are neutral then the block should be uncommented, and all items in the code block should be uncommented except for the Door(s) that the user wants blocked.  If both green and red (blocked and allowed) doors are toggled, all existing neutral are assumed blocked and commented out.  If a door is allowed (green) and all other doors are neutral, then neutral doors should be assumed blocked (red) should be commented out in the code block.  For simplicity we should output all doors of all perimeter cells by default but comment out the entire Allowed Doors block until the user toggles a perimeter tile red or green.  As a user I should see the verbose code in the Info Panel with the items commented out "//" and have the option to Copy and/or Save the shorter version by ensuring the Include Comments toggle is unchecked.
# Example A: after output w/include comments is unchecked
# Requirements Recap
# All neutral: (Neutral assumed green) Entire AllowedDoorLocations block should be commented out therefore ommiting existence of blocked doors.
# Any red (blocked) and all others neutral: Block is uncommented, all neutral items are assumed "green" and uncommented except the blocked (red) ones (which are commented).
# Both green (allowed) and red (blocked): All neutral are assumed blocked and commented out.
# Any green (allowed) and all others neutral: Neutral doors are assumed blocked (commented out), only allowed doors are uncommented.
# Default: Output all doors, but comment out the block until a perimeter tile is toggled.
# AllowedDoorLocations
#	[
#		[0, -1]
#		[-1, 0]
#	]
# Example B: 2x3 part - after output w/include comments is checked
#	AllowedDoorLocations
#	[
#		[-1, 2]
#		[0, 3]
#		[1, 3]
#		[2, 2]
#	]
#	BlockedTravelCells
#	[
#		[0, 0]
#		[1, 0]
#	]
# Example of Code Block from "Blocked Travel Directions" Mode for 2,3 part. (have not implemented this yet) - This should be a Mode Type similar to Doors & Paths, Mutually exclusive as it would need to occupy the same UI space.  Features should include ability to click left right top bottom values within each 64x64 tile internal to part.  Maybe arrows in each direction of the 64x64 tile.  Only Internal (not perimeter door tiles) should show this additional UI. Tiles Blocked Cells via "Doors & Paths" Should appear Grey'd out and not have the arrow UI overlayed Toggling would change the color green to red or something to indicate that direction is allowed or blocked. Default would be Green assuming all directions are enabled (nothing should be defined in the code block if all directions are enabled).  If a direction is blocked, then it should be defined in the code block.  If a direction is allowed, then it should not be defined in the code block.  For simplicity we should output all directions of all internal cells by default but commented out until the user toggles the direction to be blocked.  As a user I should see the verbose code in the Info Panel with the items commented out "//" and have the option to Copy and/or Save the shorter version by ensuring the Include Comments toggle is unchecked.
#	BlockedTravelCellDirections
#	[
#		{
#			Key = [0, 1]
#			Value = [Right]
#		}
#		{
#			Key = [1, 1]
#			Value = [Left]
#		}
#	]
# Example Code Block of Thermal Ports form a 2x2 Part with ports on all sides. Using "Thermal Ports" Mode - Notice how inherit logic is used to shorten the amount code necessary in each Directional Block.  For example., Direction is unnecessary to define in Port_Thermal_RightUp because its inheriting from Port_Thermal_TopLeft, ~/Part/^/0/BASE_THERMAL_PORT is also unnecessary to inherit because it Port_Thermal_TopLeft is already inheriting from it.  This should be the same for all ports, so that we can easily add or remove ports without having to worry about the code being too long or too short. As a user I should see the verbose code in the Info Panel with the items commented out "//" and have the option to Copy and/or Save the shorter version by ensuring the Include Comments toggle is unchecked.
# 		Port_Thermal_TopLeft : ~/Part/^/0/BASE_THERMAL_PORT
# 		{
# 			Location = [0,0]
# 			Direction = Left
# 		}
# 		Port_Thermal_LeftUp : Port_Thermal_TopLeft
# 		{
# 			Location = [0, 0]
# 			Direction = Up
# 		}
# 		Port_Thermal_RightUp : Port_Thermal_LeftUp
# 		{
# 			Location = [1, 0]
# 		}
# 		Port_Thermal_TopRight : Port_Thermal_RightUp
# 		{
# 			Direction = Right
# 		}
# 		Port_Thermal_BottomRight : Port_Thermal_TopRight
# 		{
# 			Location = [1,1]
# 		}
# 		Port_Thermal_RightDown : Port_Thermal_BottomRight
# 		{
# 			Direction = Down
# 		}
# 		Port_Thermal_LeftDown : Port_Thermal_RightDown
# 		{
# 			Location = [0,1]
# 		}
# 		Port_Thermal_BottomLeft : Port_Thermal_LeftDown
# 		{
# 			Direction = Left
# 		}
#!/usr/bin/env python3
# EasyGridLocations_PySide6_v2.py
# Requires Python 3.10+ and PySide6>=6.0
import sys, os, math
from pathlib import Path
from fractions import Fraction

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QBrush, QPen, QColor, QPixmap, QFont, QPainter, QFontMetricsF, QTransform
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QFileDialog, QComboBox,
    QDoubleSpinBox, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QSlider, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QSpinBox, QGroupBox, QPlainTextEdit
)

CELL_SIZE = 64
MAX_INTERIOR = 16
ARROW_LEN = 20

def parse_coord(s: str) -> float:
    """Parse decimal or fraction 'num/den' to float."""
    try:
        if '/' in s:
            return float(Fraction(s.strip()))
        return float(s)
    except Exception:
        return 0.0

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
        self.type_cb.addItems(["Point Marker", "Image Overlay"])
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
        self.w_sb = QSpinBox(); self.w_sb.setRange(1, self.W)
        self.h_sb = QSpinBox(); self.h_sb.setRange(1, self.H)
        form.addRow("Width (cells):", self.w_sb)
        form.addRow("Height (cells):", self.h_sb)

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
        is_img = (self.type_cb.currentText() == "Image Overlay")
        is_rel = (self.coord_cb.currentText() == "Relative")
        for w in (self.file_le, self.w_sb, self.h_sb):
            w.setVisible(is_img)
        self.file_le.parentWidget().setVisible(is_img)
        self.base_cb.setVisible(is_rel)

    def accept(self):
        name = self.name_le.text().strip()
        if not name:
            QMessageBox.warning(self, "Name required", "Please enter a name.")
            return
        typ = "image" if self.type_cb.currentText().startswith("Image") else "point"
        coord_mode = "rel" if self.coord_cb.currentText()=="Relative" else "abs"
        base = (
            self.base_cb.currentText()
            if coord_mode=="rel" else None
        )
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
        if typ=="image":
            file = self.file_le.text().strip()
            if not os.path.isfile(file):
                QMessageBox.warning(self, "File missing", "Select a valid image file.")
                return
            res["file"] = file
            res["w"], res["h"] = self.w_sb.value(), self.h_sb.value()
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
                    img_path = "default_images/red_x.png" if blocked else "default_images/arrow_green.png"
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
        self.setWindowTitle("EasyGridLocations v4")
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
        self.load_sprite_btn = QPushButton("Load Sprite")
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
        self.tree.itemSelectionChanged.connect(self._on_tree_sel)
        ctrl.addWidget(self.tree, 1)
        self.tree.hide()  # Start hidden

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
        cb = QPushButton("Copy")
        cb.clicked.connect(self.on_copy)
        ctrl.addWidget(cb)

        sv = QPushButton("Save")
        sv.clicked.connect(self.on_save)
        ctrl.addWidget(sv)

        # Toggle whether to include commented‐out lines in any copy/save
        from PySide6.QtWidgets import QCheckBox
        self.include_comments_cb = QCheckBox("Include comments")
        self.include_comments_cb.setChecked(True)
        ctrl.addWidget(self.include_comments_cb)

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
                        out.append(f"//    {{")
                        out.append(f"//        Key = [{x}, {y}]")
                        out.append(f"//        Value = [{d}]")
                        out.append(f"//    }}")
            out.append("// ]")
            return "\n".join(out)
        else:
            out = ["BlockedTravelCellDirections", "["]
            for (i, j, dirs) in entries:
                out.append(f"    {{")
                out.append(f"        Key = [{i}, {j}]")
                out.append(f"        Value = [{', '.join(dirs)}]")
                out.append(f"    }}")
            out.append("]")
            return "\n".join(out)

    def _context_copy(self):
        mode = self.mode_cb.currentText()
        if mode == "Locations":
            # Generate code for all layers (like in _gen_rules, but only the layers part)
            lines = []
            for name, L in self.layers.items():
                if name == "__sprite__":
                    continue
                p = L["params"]
                lines.append(f"{name} = {{")
                if L["type"] == "image":
                    lines.append(f'  File = "{p["file"]}"')
                    lines.append(f"  Size = [{p['size'][0]}, {p['size'][1]}]")
                lines.append(f"  Location = [{p['location'][0]}, {p['location'][1]}]")
                lines.append(f"  Rotation = {p['rotation']}")
                lines.append("}\n")
            txt = "\n".join(lines)
        else:
            raw = self.info_panel.toPlainText()
            txt = self._apply_comment_toggle(raw)
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
        if not self.scene: return
        f,_=QFileDialog.getOpenFileName(self,"Sprite",self.last_dir,"Images (*.png *.jpg *.bmp)")
        if not f: return
        self.last_dir=os.path.dirname(f)
        pix = QPixmap(f).scaled(
            self.scene.W*CELL_SIZE, self.scene.H*CELL_SIZE,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        item=QGraphicsPixmapItem(pix)
        item.setOpacity(0.7); item.setZValue(0.5)
        ox=(CELL_SIZE + (self.scene.W*CELL_SIZE-pix.width())/2)
        oy=(CELL_SIZE + (self.scene.H*CELL_SIZE-pix.height())/2)
        item.setPos(ox,oy)
        self.scene.addItem(item)
        arrow=self._make_arrow(ox+pix.width()/2, oy+pix.height()/2, 0)
        self.scene.addItem(arrow)
        name="__sprite__"
        self.layers[name]={
            "items":[item,arrow],
            "type":"image",
            "params":{
                "file":f,"size":(self.scene.W,self.scene.H),
                "location":(0,0),"rotation":0.0
            }
        }
        node=QTreeWidgetItem(self.tree,["Sprite"])
        node.setData(0,Qt.UserRole,name)
        node.setCheckState(0,Qt.Checked)
        self.tree.setCurrentItem(node)

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

    def _add_location(self,opts):
        x,y=opts["x"],opts["y"]
        if opts["coord_mode"]=="rel":
            base=opts["base"]
            bx,by=self.layers[base]["params"]["location"]
            x,y = bx+x, by+y
        px,py=(x+1)*CELL_SIZE,(y+1)*CELL_SIZE
        rot=opts["rotation"]
        name=opts["name"]
        if opts["type"]=="point":
            dot=QGraphicsEllipseItem(px-5,py-5,10,10)
            dot.setBrush(QBrush(Qt.red)); dot.setZValue(0.9)
            dot.setTransformOriginPoint(px,py)
            dot.setRotation(rot)
            arr = self._make_arrow(px,py,rot)
            self.scene.addItem(dot); self.scene.addItem(arr)
            self.layers[name]={
                "items":[dot,arr],"type":"point",
                "params":{"location":(x,y),"rotation":rot}
            }
        else:
            f=opts["file"]; w,h=opts["w"],opts["h"]
            pix = QPixmap(f).scaled(
                w*CELL_SIZE, h*CELL_SIZE,
                Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
            img=QGraphicsPixmapItem(pix); img.setOpacity(0.7); img.setZValue(0.5)
            img.setTransformOriginPoint(pix.width()/2,pix.height()/2)
            img.setRotation(rot)
            img.setPos(px - pix.width()/2, py - pix.height()/2)
            arr = self._make_arrow(px,py,rot)
            self.scene.addItem(img); self.scene.addItem(arr)
            self.layers[name]={
                "items":[img,arr],"type":"image",
                "params":{"file":f,"size":(w,h),"location":(x,y),"rotation":rot}
            }
        node=QTreeWidgetItem(self.tree,[name])
        node.setData(0,Qt.UserRole,name)
        node.setCheckState(0,Qt.Checked)
        self.tree.setCurrentItem(node)
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
        btn_remove = QPushButton("Remove Layer")
        btn_remove.clicked.connect(lambda: self._remove_layer(key))
        self.props_layout.addRow(btn_remove)
        btn_apply = QPushButton("Apply Changes")
        btn_apply.clicked.connect(lambda: self._apply_props(key))
        self.props_layout.addRow(btn_apply)

    def _apply_props(self,key):
        L=self.layers[key]; items=L["items"]; p=L["params"]
        x=parse_coord(self.p_x.text()); y=parse_coord(self.p_y.text())
        rot=self.p_rot.value()
        p["location"]=(x,y); p["rotation"]=rot
        px,py=(x+1)*CELL_SIZE,(y+1)*CELL_SIZE
        if L["type"]=="point":
            dot,arr=items
            dot.setRect(px-5,py-5,10,10)
            dot.setTransformOriginPoint(px,py)
            dot.setRotation(rot)
            self.scene.removeItem(arr)
            new_arr=self._make_arrow(px,py,rot)
            self.scene.addItem(new_arr)
            items[1]=new_arr
        else:
            img,arr=items
            pw,ph=img.pixmap().width(),img.pixmap().height()
            img.setTransformOriginPoint(pw/2,ph/2)
            img.setRotation(rot)
            img.setPos(px-pw/2, py-ph/2)
            self.scene.removeItem(arr)
            new_arr=self._make_arrow(px,py,rot)
            self.scene.addItem(new_arr)
            items[1]=new_arr
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

    def on_copy(self):
        raw = self._gen_rules()
        txt = self._apply_comment_toggle(raw)
        QApplication.clipboard().setText(txt)
        self.statusBar().showMessage("Copied")

    def on_save(self):
        raw = self._gen_rules()
        txt = self._apply_comment_toggle(raw)
        path,_ = QFileDialog.getSaveFileName(
            self, "Save .rules", self.last_dir, "Rules (*.rules)"
        )
        if not path:
            return
        if not path.endswith(".rules"):
            path += ".rules"
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)
        self.last_dir = os.path.dirname(path)
        self.statusBar().showMessage(f"Saved {path}")

    def _gen_rules(self):
        mode = self.mode_cb.currentText() if hasattr(self, "mode_cb") else "Doors & Paths"
        if mode == "Doors & Paths":
            return self._gen_doors_paths_code()
        elif mode == "Thermal Ports":
            return self._gen_thermal_ports_code()
        elif mode == "Blocked Travel Directions":
            return self._gen_blocked_travel_dirs_code()
        # Otherwise, fall back to the original output for Locations
        W,H = self.scene.W, self.scene.H
        lines=[f"size = [{W}, {H}]\n"]
        ald=[]; bld=[]
        all_door_coords = []
        for (i,j),c in self.scene.cell_states.items():
            if c["type"]=="door":
                all_door_coords.append((i, j))
        for (i,j) in all_door_coords:
            c = self.scene.cell_states[(i,j)]
            txt = f"[{i},{j}]"
            if c["state"]==1: ald.append(txt)
            elif c["state"]==0:
                ald.append(f"// {txt}")
        lines += ["AllowedDoorLocations = ["]
        for a in ald:
            lines.append(f"  {a},")
        lines.append("]\n")
        all_blocked = []
        for (i,j),c in self.scene.cell_states.items():
            if c["type"]=="blocked":
                txt = f"[{i},{j}]"
                if c["state"]==1:
                    all_blocked.append(txt)
                elif c["state"]==0:
                    all_blocked.append(f"// {txt}")
        lines += ["BlockedTravelCells = ["]
        for b in all_blocked:
            lines.append(f"  {b},")
        lines.append("]\n")

        # --- Thermal Ports (all possible, vanilla order, commented out if disabled) ---
        def vanilla_ports_all(W, H, port_status):
            ports = []
            # 1x1
            if W == 1 and H == 1:
                for dirn in ["Up", "Right", "Down", "Left"]:
                    enabled = port_status.get((0,0,dirn), False)
                    name = f"Port_Thermal_{dirn}"
                    ports.append((name, [0,0], dirn, enabled))
                return ports
            # 2x2
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
                idxs = {"Left":0, "Down":0, "Right":0, "Up":0}
                # Left
                for y in range(H):
                    n = "Port_Thermal_Left%d" % idxs["Left"]
                    idxs["Left"] += 1
                    enabled = port_status.get((0,y,"Left"), False)
                    ports.append((n, [0,y], "Left", enabled))
                # Bottom
                for x in range(1, W):
                    n = "Port_Thermal_Down%d" % idxs["Down"]
                    idxs["Down"] += 1
                    enabled = port_status.get((x,H-1,"Down"), False)
                    ports.append((n, [x,H-1], "Down", enabled))
                # Right
                for y in range(H-2, -1, -1):
                    n = "Port_Thermal_Right%d" % idxs["Right"]
                    idxs["Right"] += 1
                    enabled = port_status.get((W-1,y,"Right"), False)
                    ports.append((n, [W-1,y], "Right", enabled))
                # Top
                for x in range(W-2, 0, -1):
                    n = "Port_Thermal_Up%d" % idxs["Up"]
                    idxs["Up"] += 1
                    enabled = port_status.get((x,0,"Up"), False)
                    ports.append((n, [x,0], "Up", enabled))
                return ports

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
            # Find first enabled port
            enabled_indices = [i for i, (_, _, _, en) in enumerate(ports) if en]
            if enabled_indices:
                first_enabled = enabled_indices[0]
                prev_enabled_name = None
                for idx, (name, loc, dirn, enabled) in enumerate(ports):
                    # If this is the first enabled, always use BASE_THERMAL_PORT
                    if enabled:
                        if prev_enabled_name is None:
                            base = "~/Part/^/0/BASE_THERMAL_PORT"
                        else:
                            base = prev_enabled_name
                        block = [
                            f"{name} : {base}",
                            "{",
                            f"    Location = [{loc[0]}, {loc[1]}]",
                            f"    Direction = {dirn}",
                            "}"
                        ]
                        lines += block
                        lines.append("")
                        prev_enabled_name = name
                    else:
                        # Comment out disabled port, show what it would inherit from (find last enabled above)
                        if prev_enabled_name is None:
                            base = "~/Part/^/0/BASE_THERMAL_PORT"
                        else:
                            base = prev_enabled_name
                        block = [
                            f"// {name} : {base}",
                            "// {",
                            f"//     Location = [{loc[0]}, {loc[1]}]",
                            f"//     Direction = {dirn}",
                            "// }"
                        ]
                        lines += block
                        lines.append("")
            else:
                # All ports disabled—comment all as inheriting from BASE_THERMAL_PORT
                for idx, (name, loc, dirn, enabled) in enumerate(ports):
                    block = [
                        f"// {name} : ~/Part/^/0/BASE_THERMAL_PORT",
                        "// {",
                        f"//     Location = [{loc[0]}, {loc[1]}]",
                        f"//     Direction = {dirn}",
                        "// }"
                    ]
                    lines += block
                    lines.append("")

        for name,L in self.layers.items():
            if name=="__sprite__": continue
            p=L["params"]
            lines.append(f"{name} = {{")
            if L["type"]=="image":
                lines.append(f'  File = "{p["file"]}"')
                lines.append(f"  Size = [{p['size'][0]}, {p['size'][1]}]")
            lines.append(f"  Location = [{p['location'][0]}, {p['location'][1]}]")
            lines.append(f"  Rotation = {p['rotation']}")
            lines.append("}\n")
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

    # === Thermal Ports Code Generator ===
    def _gen_thermal_ports_code(self):
        W, H = self.scene.W, self.scene.H
        lines = []

        # --- Thermal Ports (all possible, vanilla order, commented out if disabled) ---
        def vanilla_ports_all(W, H, port_status):
            ports = []
            # 1x1
            if W == 1 and H == 1:
                for dirn in ["Up", "Right", "Down", "Left"]:
                    enabled = port_status.get((0,0,dirn), False)
                    name = f"Port_Thermal_{dirn}"
                    ports.append((name, [0,0], dirn, enabled))
                return ports
            # 2x2
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
                idxs = {"Left":0, "Down":0, "Right":0, "Up":0}
                # Left
                for y in range(H):
                    n = "Port_Thermal_Left%d" % idxs["Left"]
                    idxs["Left"] += 1
                    enabled = port_status.get((0,y,"Left"), False)
                    ports.append((n, [0,y], "Left", enabled))
                # Bottom
                for x in range(1, W):
                    n = "Port_Thermal_Down%d" % idxs["Down"]
                    idxs["Down"] += 1
                    enabled = port_status.get((x,H-1,"Down"), False)
                    ports.append((n, [x,H-1], "Down", enabled))
                # Right
                for y in range(H-2, -1, -1):
                    n = "Port_Thermal_Right%d" % idxs["Right"]
                    idxs["Right"] += 1
                    enabled = port_status.get((W-1,y,"Right"), False)
                    ports.append((n, [W-1,y], "Right", enabled))
                # Top
                for x in range(W-2, 0, -1):
                    n = "Port_Thermal_Up%d" % idxs["Up"]
                    idxs["Up"] += 1
                    enabled = port_status.get((x,0,"Up"), False)
                    ports.append((n, [x,0], "Up", enabled))
                return ports

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
                first_enabled = enabled_indices[0]
                prev_enabled_name = None
                for idx, (name, loc, dirn, enabled) in enumerate(ports):
                    # If this is the first enabled, always use BASE_THERMAL_PORT
                    if enabled:
                        if prev_enabled_name is None:
                            base = "~/Part/^/0/BASE_THERMAL_PORT"
                        else:
                            base = prev_enabled_name
                        block = [
                            f"{name} : {base}",
                            "{",
                            f"    Location = [{loc[0]}, {loc[1]}]",
                            f"    Direction = {dirn}",
                            "}"
                        ]
                        lines += block
                        lines.append("")
                        prev_enabled_name = name
                    else:
                        if prev_enabled_name is None:
                            base = "~/Part/^/0/BASE_THERMAL_PORT"
                        else:
                            base = prev_enabled_name
                        block = [
                            f"// {name} : {base}",
                            "// {",
                            f"//     Location = [{loc[0]}, {loc[1]}]",
                            f"//     Direction = {dirn}",
                            "// }"
                        ]
                        lines += block
                        lines.append("")
            else:
                # All ports disabled—comment all as inheriting from BASE_THERMAL_PORT
                for idx, (name, loc, dirn, enabled) in enumerate(ports):
                    block = [
                        f"// {name} : ~/Part/^/0/BASE_THERMAL_PORT",
                        "// {",
                        f"//     Location = [{loc[0]}, {loc[1]}]",
                        f"//     Direction = {dirn}",
                        "// }"
                    ]
                    lines += block
                    lines.append("")

        return "\n".join(lines)


if __name__=="__main__":
    app=QApplication(sys.argv)
    win=MainWindow(); win.resize(1200,800); win.show()
    sys.exit(app.exec())
