#!/usr/bin/env python3
# pip install PySide6 Pillow

import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog,
    QTextEdit, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from PIL import Image

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cosmoteer Decals List Generator")
        self._build_ui()

    def _build_ui(self):
        w = QWidget()
        self.setCentralWidget(w)
        vlay = QVBoxLayout(w)

        # Folder selector
        hlay1 = QHBoxLayout()
        hlay1.addWidget(QLabel("Target Folder:"))
        self.folder_edit = QLineEdit()
        hlay1.addWidget(self.folder_edit, 1)
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self._browse_folder)
        hlay1.addWidget(btn_browse)
        vlay.addLayout(hlay1)

        # Prefix field
        hlay2 = QHBoxLayout()
        hlay2.addWidget(QLabel("Enter a Prefix:"))
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("e.g. sw_")
        hlay2.addWidget(self.prefix_edit, 1)
        vlay.addLayout(hlay2)

        # Substitutions mapping
        vlay.addWidget(QLabel("Substitutions (one mapping per line, format old=new):"))
        self.subs_edit = QTextEdit()
        self.subs_edit.setFixedHeight(80)
        vlay.addWidget(self.subs_edit)

        # Substitution targets
        hlay_sub = QHBoxLayout()
        hlay_sub.addWidget(QLabel("Apply substitutions to:"))
        self.chk_sub_old = QCheckBox("Old")
        self.chk_sub_new = QCheckBox("New")
        self.chk_sub_old.setChecked(True)
        self.chk_sub_new.setChecked(True)
        hlay_sub.addWidget(self.chk_sub_old)
        hlay_sub.addWidget(self.chk_sub_new)
        hlay_sub.addStretch()
        vlay.addLayout(hlay_sub)

        # Parameter checkboxes
        hlay3 = QHBoxLayout()
        hlay3.addWidget(QLabel("Include optional parameters:"))
        self.chk_rot = QCheckBox("Rotation")
        self.chk_flipx = QCheckBox("FlipX")
        self.chk_flipy = QCheckBox("FlipY")
        self.chk_inv = QCheckBox("Invert")
        for chk in (self.chk_rot, self.chk_flipx, self.chk_flipy, self.chk_inv):
            chk.setChecked(True)
            hlay3.addWidget(chk)
        hlay3.addStretch()
        vlay.addLayout(hlay3)

        # Generate button
        btn_gen = QPushButton("Generate decals_list.rules")
        btn_gen.clicked.connect(self._run_generation)
        vlay.addWidget(btn_gen)

        # Log window
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        vlay.addWidget(self.log, 1)

        # Help panel (rich text)
        help_html = '''
        <h3>Help</h3>
        <p><i>This tool generates per-folder &amp; master decal lists in the new Cosmoteer syntax.</i></p>
        <p><b>New entry format:</b></p>
        <pre>Upgrades
[
    { Old="plain01";    New={ ID="box"; Rot0Size=[1,1]; }; }
]</pre>
        <ul>
          <li><b>Old</b>: exact filename (no .png), substitutions if selected.</li>
          <li><b>New</b>: inner block with <code>ID</code> (prefix + filename) and <code>Rot0Size</code>.</li>
        </ul>
        <p><b>Optional commented params</b> go inside the <code>New</code> block:</p>
        <ul>
          <li><code>Rotation=X</code> (0–3)</li>
          <li><code>FlipX=true/false</code></li>
          <li><code>FlipY=true/false</code></li>
          <li><code>Invert=true/false</code></li>
        </ul>
        <p><b>Substitutions</b>:</p>
        <ul>
          <li>List mappings in <code>old=new</code> lines.</li>
          <li>Use the checkboxes to apply them to <i>Old</i>, <i>New</i>, or both.</li>
        </ul>
        <p><b>Rules:</b></p>
        <ul>
          <li>Generates a <code>decals_list.rules</code> per folder, plus a master <code>full_decals_list.rules</code>.</li>
        </ul>
        '''
        help_label = QLabel(help_html)
        help_label.setTextFormat(Qt.RichText)
        help_label.setWordWrap(True)
        vlay.addWidget(help_label)

    def _append_log(self, msg):
        self.log.append(msg)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        if folder:
            self.folder_edit.setText(folder)

    def _parse_substitutions(self):
        subs = []
        for line in self.subs_edit.toPlainText().splitlines():
            if "=" in line:
                old, new = line.split("=", 1)
                subs.append((old, new))
        return subs

    def _apply_subs(self, text, subs):
        for old, new in subs:
            text = text.replace(old, new)
        return text

    def _run_generation(self):
        root = self.folder_edit.text().strip()
        prefix = self.prefix_edit.text().strip()
        if not root or not os.path.isdir(root):
            QMessageBox.critical(self, "Error", "Please select a valid folder.")
            return

        self.log.clear()
        self.subs = self._parse_substitutions()
        self.master_entries = set()
        self._process_folder(root, prefix)

        # write master list
        if self.master_entries:
            master_path = os.path.join(root, 'full_decals_list.rules')
            try:
                with open(master_path, 'w', encoding='utf-8') as m:
                    m.write("Upgrades\n[\n")
                    for line in sorted(self.master_entries):
                        m.write(line + "\n")
                    m.write("]\n")
                self._append_log(f"[INFO] Wrote master list to: {master_path}")
            except Exception as e:
                self._append_log(f"[ERROR] Failed writing master list: {e}")

        QMessageBox.information(
            self, "Finished",
            f"Generated decals_list.rules in {self.count} folder(s)\n+ master full_decals_list.rules"
        )

    def _process_folder(self, root_folder, prefix):
        self.count = 0
        for dirpath, _, files in os.walk(root_folder):
            pngs = [f for f in files if f.lower().endswith('.png')]
            if not pngs:
                continue

            self._append_log(f"[DEBUG] Processing: {dirpath} ({len(pngs)} PNGs)")

            # sizes
            sizes = {}
            for fname in pngs:
                path = os.path.join(dirpath, fname)
                try:
                    w, h = Image.open(path).size
                    sizes[fname] = (w // 64, h // 64)
                except Exception as e:
                    sizes[fname] = (1,1)
                    self._append_log(f"[WARN] Can't open {fname}: {e}")
                QApplication.processEvents()

            # prepare mapping
            mapped = []
            for f in pngs:
                raw = os.path.splitext(f)[0]
                old_key = raw
                if self.chk_sub_old.isChecked():
                    old_key = self._apply_subs(raw, self.subs)
                new_key = raw
                if self.chk_sub_new.isChecked():
                    new_key = self._apply_subs(raw, self.subs)
                mapped.append((f, raw, old_key, new_key))

            # alignment for Old and New
            old_segs = [f'Old="{old}";' for _,_,old,_ in mapped]
            max_old = max(len(seg) for seg in old_segs)

            lines = ["Upgrades", "["]
            for orig, raw, old_key, new_key in sorted(mapped, key=lambda x: x[2].lower()):
                sx, sy = sizes[orig]
                old_seg = f'Old="{old_key}";'
                old_padded = old_seg.ljust(max_old)

                # optional params inside New block
                parts = []
                if self.chk_rot.isChecked(): parts.append("/*Rotation=1;*/")
                if self.chk_flipx.isChecked(): parts.append("/*FlipX=true;*/")
                if self.chk_flipy.isChecked(): parts.append("/*FlipY=true;*/")
                if self.chk_inv.isChecked(): parts.append("/*Invert=true;*/")
                param_str = (' ' + ' '.join(parts)) if parts else ''

                full_id = f"{prefix}{new_key}"
                new_block = f'New={{ ID="{full_id}"; Rot0Size=[{sx},{sy}];{param_str} }};'

                # two tabs after Old segment for clear separation
                line = f"    {{ {old_padded}\t\t{new_block} }}"

                # # comment if starts with digit
                # if raw and raw[0].isdigit():
                #     line = "// " + line

                lines.append(line)
                self.master_entries.add(line)

            lines.append("]")

            out_path = os.path.join(dirpath, 'decals_list.rules')
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines))
                self._append_log(f"[DEBUG] Wrote: {out_path}")
                self.count += 1
            except Exception as e:
                self._append_log(f"[ERROR] Failed to write in {dirpath}: {e}")
            QApplication.processEvents()

        self._append_log(f"[INFO] Done. {self.count} folder(s) processed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(900, 700)
    win.show()
    sys.exit(app.exec())
