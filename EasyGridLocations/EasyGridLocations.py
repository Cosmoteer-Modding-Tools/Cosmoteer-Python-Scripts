#!/usr/bin/env python3
# EasyGridLocations_PySide6.py
# Python 3.10+, PySide6

import sys
import os
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QBrush, QPen, QColor, QPixmap, QFont, QPainter,
    QFontMetricsF
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsEllipseItem,
    QGraphicsTextItem, QFileDialog, QComboBox,
    QDoubleSpinBox, QTreeWidget, QTreeWidgetItem,
    QInputDialog, QSlider, QMessageBox
)

CELL_SIZE = 64
MAX_INTERIOR = 16

class GridScene(QGraphicsScene):
    def __init__(self, width_cells, height_cells, parent=None):
        super().__init__(parent)
        self.W = width_cells
        self.H = height_cells
        # state: (i,j)->{'type':'door'/'blocked', 'state':0/1/2}
        self.cell_states = {}
        self._draw_grid()

    def _draw_grid(self):
        total_w = (self.W + 2) * CELL_SIZE
        total_h = (self.H + 2) * CELL_SIZE
        # background
        self.setSceneRect(0, 0, total_w, total_h)
        # draw cells + coordinate labels
        for i in range(self.W + 2):
            for j in range(self.H + 2):
                rect = QGraphicsRectItem(
                    i*CELL_SIZE, j*CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                rect.setPen(QPen(Qt.black))
                rect.setBrush(QBrush(Qt.white))
                self.addItem(rect)
                # coordinate label
                coord = f"{i-1},{j-1}"
                txt = QGraphicsTextItem(coord)
                txt.setFont(QFont("Consolas", 10))
                # semi-transparent so it never fully obscures sprite
                txt.setDefaultTextColor(QColor(0,0,0,160))
                # center text in cell
                fm = QFontMetricsF(txt.font())
                w = fm.horizontalAdvance(coord)
                h = fm.height()
                txt.setPos(i*CELL_SIZE + (CELL_SIZE - w)/2,
                           j*CELL_SIZE + (CELL_SIZE - h)/2)
                txt.setZValue(0.1)
                self.addItem(txt)
                is_border = i in (0, self.W+1) or j in (0, self.H+1)
                key = (i-1, j-1)  # interior coords: -1..W, -1..H
                if is_border and not ((i in (0, self.W+1) and j in (0, self.H+1))):
                    # perimeter non-corners: door state 0=none,1=allowed,2=disabled
                    self.cell_states[key] = {'type':'door','state':0,'item':rect}
                elif not is_border:
                    # interior: blocked state 0=unblocked,1=blocked
                    self.cell_states[key] = {'type':'blocked','state':0,'item':rect}
                # corners: ignore
        # offset view so interior (0,0) appears at origin
        # handled in view.translate

    def toggle_cell(self, scene_pos):
        """Toggle cell at scene_pos based on type and current mode."""
        # compute indices
        i = int(scene_pos.x() // CELL_SIZE) - 1
        j = int(scene_pos.y() // CELL_SIZE) - 1
        key = (i, j)
        if key not in self.cell_states:
            return
        cell = self.cell_states[key]
        item = cell['item']
        if cell['type'] == 'door':
            # cycle through 0 -> 1 (green) -> 2 (red) -> 0
            cell['state'] = (cell['state'] + 1) % 3
            if cell['state'] == 1:
                item.setBrush(QBrush(QColor('lightgreen')))
            elif cell['state'] == 2:
                item.setBrush(QBrush(QColor('lightcoral')))
            else:
                item.setBrush(QBrush(Qt.white))
        else:
            # interior blocked toggle
            cell['state'] ^= 1
            item.setBrush(QBrush(Qt.gray) if cell['state'] else QBrush(Qt.white))

    def mousePressEvent(self, event):
        # override to let MainWindow decide action
        super().mousePressEvent(event)
        if hasattr(self, 'click_callback'):
            self.click_callback(event.scenePos())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EasyGridLocations")
        self.setFont(QFont("Consolas", 10))
        self.last_dir = str(Path.home())
        self.layers = {}  # name -> dict with keys: item, type, params, visible, parent
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_l = QHBoxLayout(central)

        # Left: Graphics view
        self.scene = None
        self.view = QGraphicsView()
        # enable antialiasing & smooth pixmap transforms
        self.view.setRenderHints(
            self.view.renderHints()
            | QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
        )        
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        main_l.addWidget(self.view, 3)

        # Right: Controls
        ctrl = QVBoxLayout()
        main_l.addLayout(ctrl, 1)

        # Part size input
        size_h = QHBoxLayout()
        size_h.addWidget(QLabel("Part size W,H:"))
        self.size_input = QLineEdit("4,5")
        size_h.addWidget(self.size_input)
        btn_gen = QPushButton("Generate Grid")
        btn_gen.clicked.connect(self.generate_grid)
        size_h.addWidget(btn_gen)
        ctrl.addLayout(size_h)

        # Sprite overlay
        btn_sprite = QPushButton("Load Sprite")
        btn_sprite.clicked.connect(self.load_sprite)
        ctrl.addWidget(btn_sprite)

        # Mode selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Toggle Cells", "Add Location"])
        ctrl.addWidget(QLabel("Mode:"))
        ctrl.addWidget(self.mode_combo)

        # Coordinate mode
        self.coord_combo = QComboBox()
        self.coord_combo.addItems(["Direct (abs)", "Offset (from center)"])
        self.coord_combo.setToolTip(
            "Direct = absolute [x,y], Offset = relative to part center"
        )
        ctrl.addWidget(QLabel("Coordinate mode:"))
        ctrl.addWidget(self.coord_combo)

        # Rotation
        rot_h = QHBoxLayout()
        rot_h.addWidget(QLabel("Rotation:"))
        self.rot_spin = QDoubleSpinBox()
        self.rot_spin.setRange(0.0, 360.0)
        self.rot_spin.setSuffix("°")
        rot_h.addWidget(self.rot_spin)
        ctrl.addLayout(rot_h)

        # Opacity slider
        ctrl.addWidget(QLabel("Overlay opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        ctrl.addWidget(self.opacity_slider)

        # Layer/point list (tree)
        ctrl.addWidget(QLabel("Layers & Points:"))
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemChanged.connect(self.on_tree_item_changed)
        ctrl.addWidget(self.tree, 1)

        # Copy & Save
        btn_copy = QPushButton("Copy to Clipboard")
        btn_copy.clicked.connect(self.copy_code)
        btn_save = QPushButton("Save .rules")
        btn_save.clicked.connect(self.save_code)
        ctrl.addWidget(btn_copy)
        ctrl.addWidget(btn_save)

        self.statusBar().showMessage("Ready")

    def generate_grid(self):
        text = self.size_input.text()
        try:
            w, h = map(int, text.split(","))
            if not (1 <= w <= MAX_INTERIOR and 1 <= h <= MAX_INTERIOR):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid size",
                                f"Enter two integers between 1 and {MAX_INTERIOR}")
            return
        # clear previous
        self.layers.clear()
        self.tree.clear()
        scene = GridScene(w, h)
        scene.click_callback = self.on_scene_click
        self.scene = scene
        self.view.setScene(scene)
        # translate so interior cell (0,0) at origin
        self.view.resetTransform()
        self.view.translate(-CELL_SIZE, -CELL_SIZE)
        self.statusBar().showMessage(f"Grid {w}×{h} created")

    def load_sprite(self):
        if not self.scene:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Select sprite file", self.last_dir,
            "Images (*.png *.jpg *.bmp)"
        )
        if not path:
            return
        self.last_dir = os.path.dirname(path)
        pix = QPixmap(path)
        W, H = self.scene.W, self.scene.H
        # force scale to interior size (or keep aspect if you prefer)
        pix = pix.scaled(W*CELL_SIZE, H*CELL_SIZE,
                         Qt.KeepAspectRatio, Qt.SmoothTransformation)
        item = QGraphicsPixmapItem(pix)
        item.setOpacity(self.opacity_slider.value()/255.0)
        item.setZValue(0.5)
        # center within the interior (border cells = OFFSET of 1)
        offset_x = CELL_SIZE + (W*CELL_SIZE - pix.width())/2
        offset_y = CELL_SIZE + (H*CELL_SIZE - pix.height())/2
        item.setPos(offset_x, offset_y)

        self.scene.addItem(item)
        self.layers["__sprite__"] = {
            'item': item, 'type': 'image', 'params': {
                'file': path, 'size': (W, H), 'location': (0, 0),
                'rotation': 0.0
            }, 'visible': True, 'parent': None
        }
        # add to tree
        node = QTreeWidgetItem(self.tree, ["Sprite"])
        node.setData(0, Qt.UserRole, "__sprite__")
        node.setCheckState(0, Qt.Checked)
        self.statusBar().showMessage("Sprite loaded")

    def update_opacity(self, val):
        for name, layer in self.layers.items():
            if layer['type'] == 'image':
                layer['item'].setOpacity(val / 255.0)

    def on_tree_item_changed(self, item, col):
        name = item.data(0, Qt.UserRole)
        if name in self.layers:
            visible = item.checkState(0) == Qt.Checked
            self.layers[name]['item'].setVisible(visible)
            self.layers[name]['visible'] = visible

    def on_scene_click(self, scene_pos):
        if self.mode_combo.currentText() == "Toggle Cells":
            self.scene.toggle_cell(scene_pos)
        else:
            self._handle_add_location(scene_pos)

    def _handle_add_location(self, scene_pos):
        # compute logical cell coordinate
        x = scene_pos.x() / CELL_SIZE - 1
        y = scene_pos.y() / CELL_SIZE - 1
        # choose type
        typ, ok = QInputDialog.getItem(
            self, "Add", "Type:", ["Point Marker", "Image Overlay"], 0, False
        )
        if not ok:
            return
        if typ == "Point Marker":
            name, ok2 = QInputDialog.getText(self, "Point Name", "Enter name:")
            if not ok2 or not name:
                return
            # coords
            if self.coord_combo.currentIndex() == 1:
                # offset: relative to center
                cx = self.scene.W / 2 - 0.5
                cy = self.scene.H / 2 - 0.5
                rx, ry = x - cx, y - cy
            else:
                rx, ry = x, y
            rot = self.rot_spin.value()
            # draw marker
            dot = QGraphicsEllipseItem(
                scene_pos.x() - 5, scene_pos.y() - 5, 10, 10
            )
            dot.setBrush(QBrush(Qt.red))
            dot.setRotation(rot)
            dot.setZValue(1)
            self.scene.addItem(dot)
            self.layers[name] = {
                'item': dot, 'type': 'point',
                'params': {'location': (rx, ry), 'rotation': rot},
                'visible': True, 'parent': None
            }
            node = QTreeWidgetItem(self.tree, [name])
            node.setData(0, Qt.UserRole, name)
            node.setCheckState(0, Qt.Checked)

        else:
            layer_name, ok3 = QInputDialog.getText(
                self, "Layer Name", "Enter render layer name:"
            )
            if not ok3 or not layer_name:
                return
            path, _ = QFileDialog.getOpenFileName(
                self, "Image file", self.last_dir,
                "Images (*.png *.jpg *.bmp)"
            )
            if not path:
                return
            self.last_dir = os.path.dirname(path)
            w_cells, ok4 = QInputDialog.getInt(self, "Width (cells)", "W:", 1, 1, self.scene.W)
            if not ok4:
                return
            h_cells, ok5 = QInputDialog.getInt(self, "Height (cells)", "H:", 1, 1, self.scene.H)
            if not ok5:
                return
            if self.coord_combo.currentIndex() == 1:
                cx = self.scene.W / 2 - 0.5
                cy = self.scene.H / 2 - 0.5
                rx, ry = x - cx, y - cy
            else:
                rx, ry = x, y
            rot = self.rot_spin.value()
            pix = QPixmap(path).scaled(
                w_cells*CELL_SIZE, h_cells*CELL_SIZE,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            img = QGraphicsPixmapItem(pix)
            img.setOpacity(self.opacity_slider.value()/255.0)
            img.setPos((rx+1)*CELL_SIZE, (ry+1)*CELL_SIZE)
            img.setRotation(rot)
            img.setZValue(0.8)
            self.scene.addItem(img)
            self.layers[layer_name] = {
                'item': img, 'type': 'image',
                'params': {
                    'file': path, 'size': (w_cells, h_cells),
                    'location': (rx, ry), 'rotation': rot
                },
                'visible': True, 'parent': None
            }
            node = QTreeWidgetItem(self.tree, [layer_name])
            node.setData(0, Qt.UserRole, layer_name)
            node.setCheckState(0, Qt.Checked)

    def _generate_rules_text(self):
        lines = []
        # size
        lines.append(f"size = [{self.scene.W}, {self.scene.H}]\n")
        # doors
        allowed = []
        for (i, j), c in self.scene.cell_states.items():
            if c['type'] == 'door' and c['state'] == 1:
                allowed.append(f"[{i}, {j}]")
        lines.append("AllowedDoorLocations = [")
        for a in allowed:
            lines.append(f"  {a},")
        lines.append("]\n")
        # blocked
        blocked = []
        for (i, j), c in self.scene.cell_states.items():
            if c['type'] == 'blocked' and c['state'] == 1:
                blocked.append(f"[{i}, {j}]")
        lines.append("BlockedTravelCells = [")
        for b in blocked:
            lines.append(f"  {b},")
        lines.append("]\n")
        # layers
        for name, L in self.layers.items():
            if name == "__sprite__":
                continue
            p = L['params']
            lines.append(f"{name} = {{")
            if L['type'] == 'image':
                lines.append(f'  File = "{p["file"]}"')
                lines.append(f"  Size = [{p['size'][0]}, {p['size'][1]}]")
            lines.append(f"  Location = [{p['location'][0]}, {p['location'][1]}]")
            lines.append(f"  Rotation = {p['rotation']}")
            lines.append("}\n")
        return "\n".join(lines)

    def copy_code(self):
        txt = self._generate_rules_text()
        QApplication.clipboard().setText(txt)
        self.statusBar().showMessage("Code copied to clipboard")

    def save_code(self):
        txt = self._generate_rules_text()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save .rules file", self.last_dir, "Rules (*.rules)"
        )
        if not path:
            return
        self.last_dir = os.path.dirname(path)
        if not path.endswith(".rules"):
            path += ".rules"
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)
        self.statusBar().showMessage(f"Saved to {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1200, 800)
    win.show()
    sys.exit(app.exec())
