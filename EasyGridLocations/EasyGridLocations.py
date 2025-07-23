#!/usr/bin/env python3
# EasyGridLocations_PySide6_v2.py
# Requires Python 3.10+ and PySide6>=6.0
import sys, os, math
from pathlib import Path
from fractions import Fraction

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QBrush, QPen, QColor, QPixmap, QFont, QPainter, QFontMetricsF
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QFileDialog, QComboBox,
    QDoubleSpinBox, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QSlider, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QSpinBox, QGroupBox
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
    def __init__(self, W, H, parent=None):
        super().__init__(parent)
        self.W, self.H = W, H
        self.cell_states = {}   # (i,j)->{'type','state','rect'}
        self._draw_grid()

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
        if hasattr(self, "click_cb"):
            self.click_cb(ev.scenePos())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EasyGridLocations v2")
        self.setFont(QFont("Consolas", 10))
        self.last_dir = str(Path.home())
        self.layers = {}   # name -> {'items':[], 'type','params'}
        self._build_ui()
        self.thermal_ports = {}

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
        btn = QPushButton("Load Sprite"); btn.clicked.connect(self.on_sprite)
        ctrl.addWidget(btn)
        ctrl.addWidget(QLabel("Mode:"))
        self.mode_cb=QComboBox(); self.mode_cb.addItems(
            ["Toggle Cells", "Add Location", "Thermal Ports"]
        ); ctrl.addWidget(self.mode_cb)
        self.mode_cb.currentIndexChanged.connect(self._mode_changed)
        ctrl.addWidget(QLabel("Global coord mode:"))
        self.global_coord_cb=QComboBox()
        self.global_coord_cb.addItems(["Direct","Offset"])
        ctrl.addWidget(self.global_coord_cb)
        ctrl.addWidget(QLabel("Layers & Points:"))
        self.tree=QTreeWidget(); self.tree.setHeaderHidden(True)
        self.tree.itemSelectionChanged.connect(self._on_tree_sel)
        ctrl.addWidget(self.tree,1)
        ctrl.addWidget(QLabel("Properties:"))
        self.props_box=QGroupBox(); self.props_layout=QFormLayout()
        self.props_box.setLayout(self.props_layout)
        ctrl.addWidget(self.props_box)
        self.props_box.hide()
        cb=QPushButton("Copy"); cb.clicked.connect(self.on_copy)
        sv=QPushButton("Save"); sv.clicked.connect(self.on_save)
        ctrl.addWidget(cb); ctrl.addWidget(sv)
        self.statusBar().showMessage("Ready")

    def _mode_changed(self):
        mode = self.mode_cb.currentText()
        if mode == "Thermal Ports":
            self._draw_thermal_ports()
        else:
            if hasattr(self, "_port_items"):
                for item in self._port_items:
                    self.scene.removeItem(item)
                self._port_items = []

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
        self.scene.click_cb=self._on_click
        self.view.setScene(self.scene)
        self.view.resetTransform(); self.view.translate(-CELL_SIZE,-CELL_SIZE)
        self.statusBar().showMessage(f"Grid {w}×{h}")

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
        if mode == "Toggle Cells":
            self.scene.toggle_cell(pos)
        elif mode == "Add Location":
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

    def on_copy(self):
        txt=self._gen_rules(); QApplication.clipboard().setText(txt)
        self.statusBar().showMessage("Copied")

    def on_save(self):
        txt=self._gen_rules()
        path,_=QFileDialog.getSaveFileName(
            self,"Save .rules",self.last_dir,"Rules (*.rules)"
        )
        if not path: return
        if not path.endswith(".rules"): path+=".rules"
        with open(path,"w",encoding="utf-8") as f: f.write(txt)
        self.last_dir=os.path.dirname(path)
        self.statusBar().showMessage(f"Saved {path}")

    def _gen_rules(self):
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

if __name__=="__main__":
    app=QApplication(sys.argv)
    win=MainWindow(); win.resize(1200,800); win.show()
    sys.exit(app.exec())
