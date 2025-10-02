# Folders in ./assets:
#   hole_punch/   64px stencils (opaque = HOLE, transparent = no hole). Names like A_33.png, B_66.png, etc.
#   hole_covers/  64px covers   (same names as punch, same orientation applied).
#   scorches/     128px stamps (any names). Scaled <= 1.0, any rotation.
#   shrapnel/     128px stamps (any names). Scaled <= 1.0, any rotation.
#
# Z-order: Z3 scorches | Z2 shrapnel | Z1 base with real holes | Z0 covers inside holes
# Holes never affect already-transparent base pixels.
# Presets/levels: 33, 50 (mix of 33/66), 66 with the densities you specified.
#
import os, sys, random
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List

from PySide6.QtCore import Qt, QTimer, QSize, QEvent, QSettings, QThread
from PySide6.QtGui import QImage, QPixmap, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout,
    QGroupBox, QFormLayout, QPushButton, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QLineEdit, QMessageBox, QSplashScreen
)

from PIL import Image, ImageOps, ImageChops, ImageFilter

# -----------------------------
# Utils
# -----------------------------
def rsrc(rel: str) -> str:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return str(base / rel)

def qpm(img: Image.Image) -> QPixmap:
    if img.mode != "RGBA": img = img.convert("RGBA")
    qimg = QImage(img.tobytes("raw","RGBA"), img.width, img.height, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimg)

def ensure_rgba(img: Image.Image) -> Image.Image:
    return img if img.mode == "RGBA" else img.convert("RGBA")

def scan_folder_images(folder: str):
    p = Path(folder)
    if not p.exists(): return []
    return [f for f in p.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp")]

def group_stencils_by_suffix(folder: str, suffix: str):
    out = {}
    for f in scan_folder_images(folder):
        stem = f.stem
        if stem.endswith("_"+suffix):
            key = stem.rsplit("_", 1)[0]
            out[key] = f
    return out

def load_tiled_rgba_images(path: Path, tile_sizes=(64, 128)) -> List[Image.Image]:
    path = Path(path)
    tiles: List[Image.Image] = []
    try:
        with Image.open(str(path)) as src:
            src = ensure_rgba(src)
            src.load()
            w, h = src.size
            chosen = None
            for size in tile_sizes:
                if w >= size and h >= size and w % size == 0 and h % size == 0:
                    chosen = size
                    break
            if chosen is None:
                tiles.append(src.copy())
            else:
                for top in range(0, h, chosen):
                    for left in range(0, w, chosen):
                        box = (left, top, left + chosen, top + chosen)
                        if box[2] <= w and box[3] <= h:
                            tile = src.crop(box)
                            if tile.size == (chosen, chosen):
                                tiles.append(tile.copy())
                if not tiles:
                    tiles.append(src.copy())
    except Exception:
        return tiles
    return tiles

def rotate_90(img: Image.Image, k: int) -> Image.Image:
    k %= 4
    if k == 0: return img
    if k == 1: return img.transpose(Image.ROTATE_90)
    if k == 2: return img.transpose(Image.ROTATE_180)
    return img.transpose(Image.ROTATE_270)

# -----------------------------
# Core image ops
# -----------------------------
def soft_erase(base: Image.Image, hole_mask_white: Image.Image) -> Image.Image:
    """Erase base alpha where mask is white (binary 0/255)."""
    base = ensure_rgba(base); m = hole_mask_white.convert("L")
    inv = ImageOps.invert(m)
    r,g,b,a = base.split()
    a = ImageChops.multiply(a, inv)
    return Image.merge("RGBA",(r,g,b,a))

def add_burn_rim(base: Image.Image, hole_mask_white: Image.Image, width_px: int, darkness: float) -> Image.Image:
    """Dark rim just at the hole edge; does NOT dim the rest."""
    if width_px<=0 or darkness<=0: return base
    blur = hole_mask_white.filter(ImageFilter.GaussianBlur(radius=width_px))
    ring = ImageChops.subtract(blur, hole_mask_white)  # white along edge
    ring = ring.filter(ImageFilter.GaussianBlur(radius=max(1, width_px//2)))
    rim = Image.new("RGBA", base.size, (0,0,0,0)); rim.putalpha(ring)
    dark = ImageChops.darker(base, rim)
    return Image.blend(base, dark, darkness)

def stamp_layer(base_size, stamps, count, min_scale, max_scale, max_rot, strength, seed, restrict_mask_white):
    W,H = base_size
    rnd = random.Random(seed)
    layer = Image.new("RGBA",(W,H),(0,0,0,0))
    if not stamps or count <= 0 or strength <= 0: return layer

    for _ in range(count):
        s = rnd.choice(stamps).convert("RGBA")
        s_factor = min(1.0, max(min_scale, min(max_scale, rnd.uniform(min_scale, max_scale))))
        nw = max(1, int(s.width * s_factor)); nh = max(1, int(s.height * s_factor))
        s2 = s.resize((nw, nh), Image.LANCZOS)
        ang = rnd.uniform(-max_rot, max_rot)
        s2 = s2.rotate(ang, expand=True, resample=Image.BICUBIC)
        x = rnd.randint(-nw//2, W - nw//2)
        y = rnd.randint(-nh//2, H - nh//2)
        r,g,b,a = s2.split()
        a = a.point(lambda v: int(v * strength))
        s2 = Image.merge("RGBA",(r,g,b,a))
        layer.alpha_composite(s2, (x,y))

    if restrict_mask_white is not None:
        m = restrict_mask_white.convert("L")
        keep = m.point(lambda v: 255 if v >= 128 else 0)
        r,g,b,a = layer.split()
        a = ImageChops.multiply(a, keep)
        layer = Image.merge("RGBA",(r,g,b,a))

    return layer

# -----------------------------
# Stencil-based holes (limit to non-transparent base)
# -----------------------------
def apply_stencil_holes(base: Image.Image,
                        punch_map: dict,
                        cover_map: dict,
                        tile_size: int,
                        density: float,
                        seed: int,
                        rim_w: int,
                        rim_dark: float,
                        base_alpha_init: Image.Image):
    """
    Returns (result_base_with_holes, holes_mask_white, cover_layer_rgba).
    Only changes where base_alpha_init > 0.
    """
    # rnd = random.Random(seed)
    W,H = base.size
    result = ensure_rgba(base).copy()
    holes_mask = Image.new("L",(W,H),0)
    cover_layer = Image.new("RGBA",(W,H),(0,0,0,0))

    keys = sorted(set(punch_map.keys()) & set(cover_map.keys()))
    if not keys:
        return result, holes_mask, cover_layer

    cols = (W + tile_size - 1) // tile_size
    rows = (H + tile_size - 1) // tile_size

    for gy in range(rows):
        for gx in range(cols):
            # per-cell RNG: same seed + cell coords = stable, additive
            cell_seed = (seed << 20) ^ (gx * 73856093) ^ (gy * 19349663)
            rng = random.Random(cell_seed)
    
            # include if r <= density (additive when density increases)
            if rng.random() > density:
                continue
            
            # keys are pre-sorted; stable index
            key = keys[rng.randrange(len(keys))]
    
            # LOAD the images BEFORE rotating (this was missing)
            p_img = Image.open(punch_map[key]).convert("RGBA")
            c_img = Image.open(cover_map[key]).convert("RGBA")
    
            # stable rotation in 90° steps
            k = rng.randrange(4)
            if k:
                p_img = rotate_90(p_img, k)
                c_img = rotate_90(c_img, k)
    
            # cell box
            x0 = gx*tile_size; y0 = gy*tile_size
            x1 = min(x0+tile_size, W); y1 = min(y0+tile_size, H)
            cw, ch = x1-x0, y1-y0
            if p_img.size != (cw,ch):
                p_img = p_img.crop((0,0,cw,ch))
                c_img = c_img.crop((0,0,cw,ch))
    
            # Opaque in punch -> HOLE (binary), then limit to where base had pixels
            a = p_img.split()[-1]
            tile_hole = a.point(lambda v: 255 if v >= 8 else 0)
    
            base_a_cell = base_alpha_init.crop((x0,y0,x1,y1)).point(lambda v: 255 if v>0 else 0)
            tile_hole = ImageChops.multiply(tile_hole, base_a_cell)  # prevent holes over empty base
    
            holes_mask.paste(tile_hole, (x0,y0))
    
            # Cover only inside the hole pixels & only where base existed
            cov = c_img.copy()
            cr,cg,cb,ca = cov.split()
            ca = ImageChops.multiply(ca, tile_hole)
            cov = Image.merge("RGBA",(cr,cg,cb,ca))
            cover_layer.alpha_composite(cov, (x0,y0))

    result = soft_erase(result, holes_mask)
    result = add_burn_rim(result, holes_mask, rim_w, rim_dark)

    # Clamp covers to original base area (safety)
    r,g,b,a = cover_layer.split()
    a = ImageChops.multiply(a, base_alpha_init.point(lambda v: 255 if v>0 else 0))
    cover_layer = Image.merge("RGBA",(r,g,b,a))

    return result, holes_mask, cover_layer

# -----------------------------
# Parameters (defaults per your spec, level=33)
# -----------------------------
@dataclass
class Params:
    # Holes
    hole_density: float = 0.20   # 33 default
    rim_w: int = 0
    rim_dark: float = 0.0
    # Scorches
    scorch_density: float = 0.20
    scorch_severity: float = 0.90
    scorch_min_scale: float = 0.50
    scorch_max_scale: float = 1.00
    scorch_max_rot: float = 180.0
    # Shrapnel
    shrap_density: float = 0.10
    shrap_severity: float = 0.85
    shrap_min_scale: float = 0.05
    shrap_max_scale: float = 0.30
    shrap_max_rot: float = 180.0
    shrap_set: str = "Default"
    # Misc
    seed: int = 1337
    damage_level: str = "33"     # "33" | "50" | "66"
    cover_set: str = "Steel"   # Default uses only root-level covers

# -----------------------------
# Main pipeline (adds 50 mix)
# -----------------------------
def apply_pipeline(base: Image.Image, assets_root: str, p: Params,
                   enable_holes: bool, enable_scorches: bool, enable_shrapnel: bool,
                   cover_maps: Optional[dict] = None,
                   shrap_tiles: Optional[List[Image.Image]] = None):
    W,H = base.size
    base_rgba = ensure_rgba(base)
    base_alpha_init = base_rgba.split()[-1]

    root = Path(assets_root)
    punch33 = group_stencils_by_suffix(str(root / "hole_punch"), "33")
    if cover_maps is None:
        cover33 = group_stencils_by_suffix(str(root / "hole_covers"), "33")
        cover66 = group_stencils_by_suffix(str(root / "hole_covers"), "66")
    else:
        cover33 = cover_maps.get("33", {})
        cover66 = cover_maps.get("66", {})
    punch66 = group_stencils_by_suffix(str(root / "hole_punch"), "66")

    scorch_imgs = [ensure_rgba(Image.open(str(f))) for f in scan_folder_images(str(root / "scorches"))]
    if shrap_tiles is None:
        shrap_tiles = []
        shrap_root = root / "shrapnel"
        for f in scan_folder_images(str(shrap_root)):
            shrap_tiles.extend(load_tiled_rgba_images(f))
    shrap_imgs = list(shrap_tiles)

    tile_size = 64
    for f in list(punch33.values()) + list(punch66.values()):
        tile_size = Image.open(str(f)).size[0]; break

    result = base_rgba.copy()

    # Holes + covers
    if enable_holes:
        if p.damage_level == "33" and punch33 and cover33:
            result, holes_mask, covers_layer = apply_stencil_holes(
                result, punch33, cover33, tile_size, p.hole_density, p.seed,
                p.rim_w, p.rim_dark, base_alpha_init=base_alpha_init
            )
        elif p.damage_level == "66" and punch66 and cover66:
            result, holes_mask, covers_layer = apply_stencil_holes(
                result, punch66, cover66, tile_size, p.hole_density, p.seed,
                p.rim_w, p.rim_dark, base_alpha_init=base_alpha_init
            )
        elif p.damage_level == "50":
            holes_mask = Image.new("L",(W,H),0)
            covers_layer = Image.new("RGBA",(W,H),(0,0,0,0))
            # half density from 33, half from 66 (adjust if you prefer 60/40)
            if punch33 and cover33:
                result, hm1, cov1 = apply_stencil_holes(
                    result, punch33, cover33, tile_size, p.hole_density*0.5, p.seed ^ 0x33,
                    p.rim_w, p.rim_dark, base_alpha_init=base_alpha_init
                )
                holes_mask = ImageChops.lighter(holes_mask, hm1)
                covers_layer.alpha_composite(cov1)
            if punch66 and cover66:
                # rim 0 here to avoid double darkening
                result, hm2, cov2 = apply_stencil_holes(
                    result, punch66, cover66, tile_size, p.hole_density*0.5, p.seed ^ 0x66,
                    0, 0.0, base_alpha_init=base_alpha_init
                )
                holes_mask = ImageChops.lighter(holes_mask, hm2)
                covers_layer.alpha_composite(cov2)
        else:
            holes_mask = Image.new("L",(W,H),0)
            covers_layer = Image.new("RGBA",(W,H),(0,0,0,0))
    else:
        holes_mask = Image.new("L",(W,H),0)
        covers_layer = Image.new("RGBA",(W,H),(0,0,0,0))

    # Stamps over non-transparent pixels (post-holes)
    base_alpha_after = result.split()[-1]
    stamp_mask = base_alpha_after.point(lambda v: 255 if v>0 else 0)

    area_scale = max(1, int((W*H)/(128*128)))
    # Shrapnel (Z2)
    shrap_count = int(p.shrap_density * 10 * area_scale)
    if enable_shrapnel and shrap_imgs and shrap_count>0:
        shrap_layer = stamp_layer((W,H), shrap_imgs, shrap_count,
                                  p.shrap_min_scale, p.shrap_max_scale, p.shrap_max_rot,
                                  p.shrap_severity, seed=p.seed ^ 0x222, restrict_mask_white=stamp_mask)
        result.alpha_composite(shrap_layer)
    # Scorches (Z3)
    scorch_count = int(p.scorch_density * 10 * area_scale)
    if enable_scorches and scorch_imgs and scorch_count>0:
        scorch_layer = stamp_layer((W,H), scorch_imgs, scorch_count,
                                   p.scorch_min_scale, p.scorch_max_scale, p.scorch_max_rot,
                                   p.scorch_severity, seed=p.seed ^ 0x444, restrict_mask_white=stamp_mask)
        result.alpha_composite(scorch_layer)

    # Paste covers into holes last
    result.alpha_composite(covers_layer)

    return result

# -----------------------------
# GUI
# -----------------------------
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cosmoteer Image Destroyer v1.4")

        self.assets_root = rsrc("assets")
        self.base = None
        self.params = Params()
        self.cover_always = {"33": {}, "66": {}}
        self.cover_sets = {}
        self._cover_dir_stamp = None
        self.shrap_always = []
        self.shrap_sets = {}
        self._shrap_dir_stamp = None
        self.preview_img = None
        self.settings = QSettings("CosmoteerTools", "ImageDestroyer") # remember last used directories

        central = QWidget(); self.setCentralWidget(central)

        # Timer must exist before we might call _set_level (which triggers a refresh)
        self.timer = QTimer(self); self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.refresh)

        h = QHBoxLayout(central)
        h.addWidget(self._build_controls(), 0)
        h.addWidget(self._build_preview(), 1)

        # Apply current level defaults and render
        self._set_level()       # safe now (timer+widgets exist)
        self.timer.start(10)

    def _default_dir(self) -> str:
        # Start in the user's last-opened dir, else the current working dir
        return os.path.abspath(self.settings.value("last_dir", os.getcwd()))
    
    def _last_open_dir(self) -> str:
        return os.path.abspath(self.settings.value("last_open_dir", self._default_dir()))
    
    def _last_save_dir(self) -> str:
        return os.path.abspath(self.settings.value("last_save_dir", self._default_dir()))
    
    def _set_last_open_dir(self, path: str) -> None:
        d = os.path.dirname(path) if os.path.splitext(path)[1] else path
        self.settings.setValue("last_open_dir", d)
        self.settings.setValue("last_save_dir", d)
        self.settings.setValue("last_dir", d)
    
    def _set_last_save_dir(self, path: str) -> None:
        d = os.path.dirname(path) if os.path.splitext(path)[1] else path
        self.settings.setValue("last_save_dir", d)
        self.settings.setValue("last_dir", d)
    
    def _build_preview(self):
        box = QVBoxLayout(); w = QWidget(); w.setLayout(box)
        self.preview = QLabel("Drop a PNG here or click Load Base…")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(QSize(520,520))
        self.preview.setAcceptDrops(True); self.preview.installEventFilter(self)
        self.preview.setStyleSheet("background:#1f1f1f; color:#bbb; border:1px solid #444;")
        box.addWidget(self.preview, 1)
        row = QHBoxLayout()
        b_load = QPushButton("Load Base…"); b_load.clicked.connect(self.on_load_base)
        b_save = QPushButton("Save Result…"); b_save.clicked.connect(self.on_save)
        row.addWidget(b_load); row.addWidget(b_save); row.addStretch()
        box.addLayout(row)
        return w

    def _build_controls(self):
        root = QVBoxLayout(); w = QWidget(); w.setLayout(root)

        gA = QGroupBox("Assets"); fA = QFormLayout(); gA.setLayout(fA)
        self.le_base = QLineEdit(); bb = QPushButton("Browse…"); bb.clicked.connect(self.on_load_base)
        hb = QHBoxLayout(); hb.addWidget(self.le_base,1); hb.addWidget(bb)
        fA.addRow("Base", hb)

        self.cb_level = QComboBox(); self.cb_level.addItems(["33","50","66"])
        self.cb_level.currentIndexChanged.connect(self._set_level)
        fA.addRow("Damage level", self.cb_level)

        self.le_assets = QLineEdit(self.assets_root); self.le_assets.setReadOnly(True)
        fA.addRow("Assets root", self.le_assets)
        root.addWidget(gA)

        gH = QGroupBox("Holes"); fH = QFormLayout(); gH.setLayout(fH)
        self.en_holes = QCheckBox("Enable holes"); self.en_holes.setChecked(True)
        self.sp_density = QDoubleSpinBox(); self.sp_density.setRange(0,1); self.sp_density.setSingleStep(0.05); self.sp_density.setValue(self.params.hole_density)
        self.sp_rimw = QSpinBox(); self.sp_rimw.setRange(0,64); self.sp_rimw.setValue(self.params.rim_w)
        self.sp_rimd = QDoubleSpinBox(); self.sp_rimd.setRange(0,1); self.sp_rimd.setSingleStep(0.05); self.sp_rimd.setValue(self.params.rim_dark)
        for wdg in (self.en_holes, self.sp_density, self.sp_rimw, self.sp_rimd):
            if hasattr(wdg,'stateChanged'): wdg.stateChanged.connect(lambda *_: self.timer.start(30))
            else: wdg.valueChanged.connect(lambda *_: self.timer.start(30))
        self.cb_cover_set = QComboBox()
        self.cb_cover_set.currentIndexChanged.connect(self._on_cover_set_changed)
        fH.addRow(self.en_holes)
        fH.addRow("Tile density (0..1)", self.sp_density)
        fH.addRow("Rim width", self.sp_rimw)
        fH.addRow("Rim darkness", self.sp_rimd)
        fH.addRow("Asset set", self.cb_cover_set)
        root.addWidget(gH)

        gS = QGroupBox("Scorches"); fS = QFormLayout(); gS.setLayout(fS)
        self.en_scorches = QCheckBox("Enable scorches"); self.en_scorches.setChecked(True)
        self.sp_sdens = QDoubleSpinBox(); self.sp_sdens.setRange(0,1); self.sp_sdens.setSingleStep(0.05); self.sp_sdens.setValue(self.params.scorch_density)
        self.sp_ssev  = QDoubleSpinBox(); self.sp_ssev.setRange(0,1); self.sp_ssev.setSingleStep(0.05); self.sp_ssev.setValue(self.params.scorch_severity)
        self.sp_smin  = QDoubleSpinBox(); self.sp_smin.setRange(0.05,1.0); self.sp_smin.setSingleStep(0.05); self.sp_smin.setValue(self.params.scorch_min_scale)
        self.sp_smax  = QDoubleSpinBox(); self.sp_smax.setRange(0.05,1.0); self.sp_smax.setSingleStep(0.05); self.sp_smax.setValue(self.params.scorch_max_scale)
        self.sp_srot  = QDoubleSpinBox(); self.sp_srot.setRange(0,180); self.sp_srot.setSingleStep(5.0); self.sp_srot.setValue(self.params.scorch_max_rot)
        for wdg in (self.en_scorches, self.sp_sdens, self.sp_ssev, self.sp_smin, self.sp_smax, self.sp_srot):
            if hasattr(wdg,'stateChanged'): wdg.stateChanged.connect(lambda *_: self.timer.start(30))
            else: wdg.valueChanged.connect(lambda *_: self.timer.start(30))
        fS.addRow(self.en_scorches)
        fS.addRow("Density", self.sp_sdens)
        fS.addRow("Severity", self.sp_ssev)
        fS.addRow("Min scale", self.sp_smin)
        fS.addRow("Max scale", self.sp_smax)
        fS.addRow("Max rotation", self.sp_srot)
        root.addWidget(gS)

        gP = QGroupBox("Shrapnel"); fP = QFormLayout(); gP.setLayout(fP)
        self.en_shrap = QCheckBox("Enable shrapnel"); self.en_shrap.setChecked(False)
        self.sp_pdens = QDoubleSpinBox(); self.sp_pdens.setRange(0,1); self.sp_pdens.setSingleStep(0.05); self.sp_pdens.setValue(self.params.shrap_density)
        self.sp_psev  = QDoubleSpinBox(); self.sp_psev.setRange(0,1); self.sp_psev.setSingleStep(0.05); self.sp_psev.setValue(self.params.shrap_severity)
        self.sp_pmin  = QDoubleSpinBox(); self.sp_pmin.setRange(0.05,1.0); self.sp_pmin.setSingleStep(0.05); self.sp_pmin.setValue(self.params.shrap_min_scale)
        self.sp_pmax  = QDoubleSpinBox(); self.sp_pmax.setRange(0.05,1.0); self.sp_pmax.setSingleStep(0.05); self.sp_pmax.setValue(self.params.shrap_max_scale)
        self.sp_prot  = QDoubleSpinBox(); self.sp_prot.setRange(0,180); self.sp_prot.setSingleStep(5.0); self.sp_prot.setValue(self.params.shrap_max_rot)
        self.cb_shrap_set = QComboBox(); self.cb_shrap_set.currentIndexChanged.connect(self._on_shrap_set_changed)
        for wdg in (self.en_shrap, self.sp_pdens, self.sp_psev, self.sp_pmin, self.sp_pmax, self.sp_prot):
            if hasattr(wdg,'stateChanged'): wdg.stateChanged.connect(lambda *_: self.timer.start(30))
            else: wdg.valueChanged.connect(lambda *_: self.timer.start(30))
        fP.addRow(self.en_shrap)
        fP.addRow("Asset set", self.cb_shrap_set)
        fP.addRow("Density", self.sp_pdens)
        fP.addRow("Severity", self.sp_psev)
        fP.addRow("Min scale", self.sp_pmin)
        fP.addRow("Max scale", self.sp_pmax)
        fP.addRow("Max rotation", self.sp_prot)
        root.addWidget(gP)

        row = QHBoxLayout()
        self.sp_seed = QSpinBox(); self.sp_seed.setRange(0, 2**31-1); self.sp_seed.setValue(self.params.seed)
        self.btn_reroll = QPushButton("Reroll"); self.btn_reroll.clicked.connect(self._reroll)
        lbl = QLabel("Seed:")
        row.addWidget(lbl); row.addWidget(self.sp_seed); row.addWidget(self.btn_reroll); row.addStretch()
        root.addLayout(row)

        self._populate_shrap_sets(force=True)
        self._populate_cover_sets(force=True)
        root.addStretch(); return w

    @staticmethod
    def _format_cover_label(name: str) -> str:
        cleaned = name.replace("_", " ").replace("-", " ").strip()
        return cleaned.title() if cleaned else name.title()

    def _populate_shrap_sets(self, force: bool = False) -> None:
        shrap_root = Path(self.assets_root) / "shrapnel"
        exists = shrap_root.exists()
        entries = []
        root_stat = None
        if exists:
            try:
                root_stat = shrap_root.stat()
            except OSError:
                root_stat = None
            try:
                entries = list(shrap_root.iterdir())
            except OSError:
                entries = []
        root_stamp = getattr(root_stat, "st_mtime_ns", None) if root_stat is not None else None

        file_stamps = []
        dir_stamps = []
        for entry in entries:
            try:
                entry_stat = entry.stat()
            except OSError:
                continue
            stamp = getattr(entry_stat, "st_mtime_ns", None)
            if entry.is_file():
                file_stamps.append((entry.name, stamp, getattr(entry_stat, "st_size", None)))
            elif entry.is_dir():
                dir_stamps.append((entry.name, stamp))

        stamp = (root_stamp, tuple(sorted(file_stamps)), tuple(sorted(dir_stamps)))
        if not force and stamp == self._shrap_dir_stamp:
            return
        self._shrap_dir_stamp = stamp

        always_tiles: List[Image.Image] = []
        for entry in entries:
            if entry.is_file():
                always_tiles.extend(load_tiled_rgba_images(entry))
        self.shrap_always = always_tiles

        shrap_sets = {}
        for sub in sorted((p for p in entries if p.is_dir()), key=lambda p: p.name.lower()):
            tiles: List[Image.Image] = []
            for img_path in scan_folder_images(str(sub)):
                tiles.extend(load_tiled_rgba_images(img_path))
            if tiles:
                label = self._format_cover_label(sub.name)
                shrap_sets[label] = tiles
        self.shrap_sets = shrap_sets

        desired = self.params.shrap_set if getattr(self.params, "shrap_set", None) else "Default"
        combo = getattr(self, "cb_shrap_set", None)
        if combo is None:
            return
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Default")
        for label in sorted(self.shrap_sets.keys(), key=str.casefold):
            combo.addItem(label)
        idx = combo.findText(desired)
        if idx < 0:
            idx = 0
            self.params.shrap_set = "Default"
        combo.setCurrentIndex(idx)
        combo.blockSignals(False)
        self.params.shrap_set = combo.currentText()

    def _shrap_tiles_for(self, label: str) -> List[Image.Image]:
        tiles = list(self.shrap_always)
        if label != "Default":
            tiles.extend(self.shrap_sets.get(label, []))
        return tiles

    def _on_shrap_set_changed(self, *_):
        self.params.shrap_set = self.cb_shrap_set.currentText()
        self.timer.start(30)

    def _populate_cover_sets(self, force: bool = False) -> None:
        cover_root = Path(self.assets_root) / "hole_covers"
        exists = cover_root.exists()
        root_stat = None
        entries = []
        if exists:
            try:
                root_stat = cover_root.stat()
            except OSError:
                root_stat = None
            try:
                entries = list(cover_root.iterdir())
            except OSError:
                entries = []

        stamp = None
        if exists:
            root_stamp = getattr(root_stat, "st_mtime_ns", None) if root_stat is not None else None
            sub_stamps = []
            for sub in entries:
                if sub.is_dir():
                    try:
                        sub_stat = sub.stat()
                        sub_stamp = getattr(sub_stat, "st_mtime_ns", None)
                    except OSError:
                        sub_stamp = None
                    sub_stamps.append((sub.name, sub_stamp))
            stamp = (root_stamp, tuple(sorted(sub_stamps)))

        if not force and stamp == self._cover_dir_stamp:
            return

        self._cover_dir_stamp = stamp

        if exists:
            always33 = group_stencils_by_suffix(str(cover_root), "33")
            always66 = group_stencils_by_suffix(str(cover_root), "66")
        else:
            always33 = {}
            always66 = {}
        self.cover_always = {"33": always33, "66": always66}

        cover_sets = {}
        if exists:
            subdirs = sorted((p for p in entries if p.is_dir()), key=lambda p: p.name.lower())
            for sub in subdirs:
                label = self._format_cover_label(sub.name)
                cover_sets[label] = {
                    "33": group_stencils_by_suffix(str(sub), "33"),
                    "66": group_stencils_by_suffix(str(sub), "66"),
                }
        self.cover_sets = cover_sets

        desired = self.params.cover_set if getattr(self.params, "cover_set", None) else "Default"
        self.cb_cover_set.blockSignals(True)
        self.cb_cover_set.clear()
        self.cb_cover_set.addItem("Default")
        for label in sorted(self.cover_sets.keys(), key=str.casefold):
            self.cb_cover_set.addItem(label)
        idx = self.cb_cover_set.findText(desired)
        if idx < 0:
            idx = 0
            self.params.cover_set = "Default"
        self.cb_cover_set.setCurrentIndex(idx)
        self.cb_cover_set.blockSignals(False)
        self.params.cover_set = self.cb_cover_set.currentText()

    def _cover_maps_for(self, label: str) -> dict:
        combined33 = dict(self.cover_always.get("33", {}))
        combined66 = dict(self.cover_always.get("66", {}))
        if label != "Default":
            selected = self.cover_sets.get(label)
            if selected:
                combined33.update(selected.get("33", {}))
                combined66.update(selected.get("66", {}))
        return {"33": combined33, "66": combined66}

    def _on_cover_set_changed(self, *_):
        self.params.cover_set = self.cb_cover_set.currentText()
        self.timer.start(30)

    # --- events ---
    def eventFilter(self, obj, ev):
        if obj is self.preview:
            if ev.type()==QEvent.DragEnter and ev.mimeData().hasUrls():
                ev.acceptProposedAction(); return True
            elif ev.type()==QEvent.Drop:
                url = ev.mimeData().urls()[0]
                p = url.toLocalFile()
                if p:
                    self.le_base.setText(p)
                    self._set_last_open_dir(p)
                    self._load_base()
                ev.acceptProposedAction()
                return True
        return super().eventFilter(obj, ev)

    def _set_level(self):
        lvl = self.cb_level.currentText()
        self.params.damage_level = lvl

        # apply your defaults by level
        if lvl == "33":
            self.sp_density.setValue(0.20)
            self.sp_sdens.setValue(0.20)
            self.sp_pdens.setValue(0.10)
        elif lvl == "50":
            self.sp_density.setValue(0.30)
            self.sp_sdens.setValue(0.30)
            self.sp_pdens.setValue(0.15)
        elif lvl == "66":
            self.sp_density.setValue(0.40)
            self.sp_sdens.setValue(0.50)
            self.sp_pdens.setValue(0.20)

        # global defaults per spec
        self.sp_rimw.setValue(0)
        self.sp_rimd.setValue(0.0)

        self.sp_ssev.setValue(0.90)
        self.sp_smin.setValue(0.50)
        self.sp_smax.setValue(1.00)
        self.sp_srot.setValue(180.0)

        self.sp_psev.setValue(0.85)
        self.sp_pmin.setValue(0.05)
        self.sp_pmax.setValue(1.00)
        self.sp_prot.setValue(180.0)

        self.timer.start(10)

    def _reroll(self):
        self.params.seed = int(self.sp_seed.value()) ^ random.randint(1, 1<<30)
        self.sp_seed.setValue(self.params.seed)
        self.timer.start(10)

    def on_load_base(self):
        start_dir = self._last_open_dir()
        p, _ = QFileDialog.getOpenFileName(self, "Base image", start_dir,
                                           "Images (*.png *.jpg *.jpeg *.bmp *.tif)")
        if p:
            self._set_last_open_dir(p)
            self.le_base.setText(p)
            self._load_base()

    def _load_base(self):
        p = self.le_base.text().strip()
        if not p or not os.path.exists(p): QMessageBox.warning(self,"Missing","Choose a valid base image."); return
        try: self.base = Image.open(p).convert("RGBA")
        except Exception as e: QMessageBox.critical(self,"Open failed",str(e)); return
        self.timer.start(10)

    def refresh(self):
        if self.base is None:
            self.preview.setText("Load a base image to preview."); return

        # read params from UI
        self.params.hole_density = float(self.sp_density.value())
        self.params.rim_w = int(self.sp_rimw.value()); self.params.rim_dark = float(self.sp_rimd.value())
        self.params.scorch_density = float(self.sp_sdens.value()); self.params.scorch_severity = float(self.sp_ssev.value())
        self.params.scorch_min_scale = float(self.sp_smin.value()); self.params.scorch_max_scale = float(self.sp_smax.value()); self.params.scorch_max_rot = float(self.sp_srot.value())
        self.params.shrap_density = float(self.sp_pdens.value()); self.params.shrap_severity = float(self.sp_psev.value())
        self.params.shrap_min_scale = float(self.sp_pmin.value()); self.params.shrap_max_scale = float(self.sp_pmax.value()); self.params.shrap_max_rot = float(self.sp_prot.value())

        self._populate_shrap_sets()
        shrap_choice = self.cb_shrap_set.currentText() if hasattr(self, "cb_shrap_set") and self.cb_shrap_set.count() else "Default"
        self.params.shrap_set = shrap_choice
        shrap_tiles = self._shrap_tiles_for(shrap_choice)

        self._populate_cover_sets()
        cover_choice = self.cb_cover_set.currentText() if hasattr(self, "cb_cover_set") and self.cb_cover_set.count() else "Default"
        self.params.cover_set = cover_choice
        cover_maps = self._cover_maps_for(cover_choice)

        out = apply_pipeline(
            base=self.base,
            assets_root=self.assets_root,
            p=self.params,
            enable_holes=self.en_holes.isChecked(),
            enable_scorches=self.en_scorches.isChecked(),
            enable_shrapnel=self.en_shrap.isChecked(),
            cover_maps=cover_maps,
            shrap_tiles=shrap_tiles
        )
        self.preview_img = out
        self.preview.setPixmap(qpm(out).scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if self.preview_img is not None:
            self.preview.setPixmap(qpm(self.preview_img).scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_save(self):
        if self.preview_img is None:
            QMessageBox.information(self, "Nothing to save", "Generate an image first.")
            return
    
        # propose original name + _<level>.png in last save dir
        base_path = self.le_base.text().strip()
        stem = Path(base_path).stem if base_path else "result"
        proposed = os.path.join(self._last_save_dir(), f"{stem}_{self.cb_level.currentText()}.png")
    
        p, _ = QFileDialog.getSaveFileName(self, "Save PNG", proposed, "PNG (*.png)")
        if p:
            if not p.lower().endswith(".png"):
                p += ".png"
            self.preview_img.save(p, "PNG")
            self._set_last_save_dir(p)

def main():
    app = QApplication(sys.argv)

    # Splash (if the image exists)
    splash_img = rsrc("default_images/imagedestroyer_splash.png")
    splash = None
    if os.path.exists(splash_img):
        splash = QSplashScreen(QPixmap(splash_img))
        splash.show()
        QGuiApplication.processEvents()
        # Show splash for N milliseconds
        QThread.msleep(5000)  # 5000 ms = 5 seconds

    w = App()
    w.resize(1180, 740)
    w.show()

    if splash:
        splash.finish(w)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

