#TODO: This app should be able to use pyinstaller to build an exe.  I have added a build_app.bat (used in a different repo) that uses PyInstaller to build a single file exe.  I'd like to update this file to work with this particular repository and its requirements.  the venv should be in the same folder, it will still use default_images for the splash screen, etc.)
#TODO: This app should have translation functionality that is careful not to break any inline syntax/coding properties. A guide for syntax is available at (docs\Cosmoteer – Strings Guide.md) a translate button that uses a free api to translate the base file into the selected languages.
# pip install PySide6 qdarkstyle

import os
# Force qtpy to use PySide6, suppress binding warnings
os.environ['QT_API'] = 'pyside6'

import shutil
import re
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QFileDialog,
    QMessageBox, QCheckBox, QScrollArea,
    QTabWidget, QPlainTextEdit
)
from PySide6.QtCore import Qt

# Attempt to apply a dark style if available
try:
    import qdarkstyle
except ImportError:
    qdarkstyle = None

# matches lines like "Key = \"Value\"" (no semicolon)
KV_PATTERN = re.compile(
    r'^\s*'                # leading whitespace
    r'(?P<key>[^\s=]+)'    # key (no spaces or =)
    r'\s*=\s*'            # equals sign
    r'(?P<value>.+?)'       # value (lazy up to end)
    r'\s*$'                # trailing whitespace/end
)

class RulesLocalizationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rules Localization Tool")
        self.resize(1000, 700)
        # tokens: (‘blank’, raw) (‘comment’, raw) (‘section_start’, raw) (‘section_end’, raw) (‘kv’, indent, key, fullkey)
        self.base_tokens = []
        # fullkey -> base value
        self.base_map = {}
        self.language_checkboxes = {}
        self.preview_editors = {}
        self._build_ui()

    def _build_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        self.setCentralWidget(container)

        # Directory selector
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Strings Directory:"))
        self.dir_edit = QLineEdit()
        dir_layout.addWidget(self.dir_edit, 1)
        btn_dir = QPushButton("Browse…")
        btn_dir.clicked.connect(self._select_directory)
        dir_layout.addWidget(btn_dir)
        layout.addLayout(dir_layout)

        # Base file selector
        base_layout = QHBoxLayout()
        base_layout.addWidget(QLabel("Base Template (.rules):"))
        self.base_combo = QComboBox()
        self.base_combo.setEnabled(False)
        self.base_combo.currentIndexChanged.connect(self._on_base_combo_changed)
        base_layout.addWidget(self.base_combo, 1)
        layout.addLayout(base_layout)

        # Language checkboxes
        layout.addWidget(QLabel("Select languages to (re)generate:"))
        self.lang_area = QScrollArea(); self.lang_area.setWidgetResizable(True)
        self.lang_widget = QWidget(); self.lang_layout = QVBoxLayout(self.lang_widget)
        self.lang_area.setWidget(self.lang_widget)
        layout.addWidget(self.lang_area, 1)

        # Preview and apply
        btns = QHBoxLayout()
        self.btn_preview = QPushButton("Preview"); self.btn_preview.clicked.connect(self._do_preview)
        btns.addWidget(self.btn_preview)
        self.btn_apply = QPushButton("Apply Changes"); self.btn_apply.clicked.connect(self._apply_changes)
        btns.addWidget(self.btn_apply)
        layout.addLayout(btns)

        # Preview tabs
        self.tabs = QTabWidget(); layout.addWidget(self.tabs, 3)

    def _select_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Strings Directory")
        if path:
            self.dir_edit.setText(path)
            self._populate_base_combo(path)
            self._populate_language_list(path)

    def _populate_language_list(self, directory):
        for cb in self.language_checkboxes.values(): cb.deleteLater()
        self.language_checkboxes.clear()
        for fname in sorted(os.listdir(directory)):
            if fname.lower().endswith('.rules'):
                code = fname[:-6]
                cb = QCheckBox(code); cb.setChecked(True)
                self.lang_layout.addWidget(cb)
                self.language_checkboxes[code] = cb
        self.lang_layout.addStretch()

    def _populate_base_combo(self, directory):
        self.base_combo.blockSignals(True)
        self.base_combo.clear()
        self.base_tokens.clear(); self.base_map.clear()
        if os.path.isdir(directory):
            rules_files = sorted(
                fname for fname in os.listdir(directory)
                if fname.lower().endswith('.rules')
            )
        else:
            rules_files = []
        for fname in rules_files:
            full_path = os.path.join(directory, fname)
            self.base_combo.addItem(fname, full_path)
        self.base_combo.setEnabled(bool(rules_files))
        if rules_files:
            self.base_combo.setCurrentIndex(0)
        self.base_combo.blockSignals(False)
        if rules_files:
            self._load_base_file(self.base_combo.currentData())

    def _on_base_combo_changed(self, index):
        if index < 0:
            self.base_tokens.clear()
            self.base_map.clear()
            return
        path = self.base_combo.itemData(index)
        if not path:
            self.base_tokens.clear()
            self.base_map.clear()
            return
        self._load_base_file(path)

    def _load_base_file(self, path):
        """Parse base .rules into tokens and base_map"""
        self.base_tokens.clear(); self.base_map.clear()
        stack = []; pending = None
        with open(path, encoding='utf-8') as f:
            for line in f:
                raw = line.rstrip('\n')
                stripped = raw.lstrip()
                # blank
                if not stripped:
                    pending = None; self.base_tokens.append(('blank', raw)); continue
                # comment
                if stripped.startswith('//') or stripped.startswith('/*'):
                    pending = None; self.base_tokens.append(('comment', raw)); continue
                # inline section with brace
                if stripped.endswith('{') and stripped != '{':
                    # strip trailing comments
                    name = stripped[:-1].split('//',1)[0].split('/*',1)[0].strip()
                    stack.append(name); pending = None; self.base_tokens.append(('section_start', raw)); continue
                # bare brace
                if stripped == '{':
                    name = pending.split('//',1)[0].split('/*',1)[0].strip() if pending else ''
                    stack.append(name); pending = None; self.base_tokens.append(('section_start', raw)); continue
                # section name line (before brace)
                if '=' not in stripped and stripped not in ('}', '};'):
                    pending = stripped.split('//',1)[0].split('/*',1)[0].strip()
                    self.base_tokens.append(('comment', raw)); continue
                # section end
                if stripped in ('}', '};'):
                    pending = None
                    if stack: stack.pop()
                    self.base_tokens.append(('section_end', raw)); continue
                # key/value
                m = KV_PATTERN.match(raw)
                if m:
                    pending = None
                    key = m.group('key'); val = m.group('value').strip()
                    indent = raw[:len(raw)-len(stripped)]
                    fullkey = '.'.join([s for s in stack if s] + [key])
                    self.base_tokens.append(('kv', indent, key, fullkey))
                    self.base_map[fullkey] = val
                else:
                    pending = None; self.base_tokens.append(('comment', raw))

    def _parse_target(self, path):
        """Parse target .rules into fullkey->value map"""
        mapping = {}
        if not os.path.isfile(path): return mapping
        stack = []; pending = None
        with open(path, encoding='utf-8') as f:
            for line in f:
                raw = line.rstrip('\n'); stripped = raw.lstrip()
                if not stripped:
                    pending = None; continue
                if stripped.startswith('//') or stripped.startswith('/*'):
                    pending = None; continue
                if stripped.endswith('{') and stripped != '{':
                    name = stripped[:-1].split('//',1)[0].split('/*',1)[0].strip()
                    stack.append(name); pending = None; continue
                if stripped == '{':
                    name = pending.split('//',1)[0].split('/*',1)[0].strip() if pending else ''
                    stack.append(name); pending = None; continue
                if stripped in ('}', '};'):
                    pending = None
                    if stack: stack.pop()
                    continue
                # key/value
                m = KV_PATTERN.match(raw)
                if m:
                    pending = None
                    key = m.group('key'); val = m.group('value').strip()
                    fullkey = '.'.join([s for s in stack if s] + [key])
                    mapping[fullkey] = val
                else:
                    # section name line
                    if '=' not in stripped and not stripped.startswith('//'):
                        pending = stripped.split('//',1)[0].split('/*',1)[0].strip()
                    else:
                        pending = None
        print(f"[INFO] Parsed {len(mapping)} entries from {os.path.basename(path)}")
        return mapping

    def _generate_content(self, target_map):
        lines = []
        for token in self.base_tokens:
            ttype = token[0]
            if ttype in ('blank','comment','section_start','section_end'):
                lines.append(token[1])
            else:  # kv
                _, indent, key, fullkey = token
                val = target_map.get(fullkey, self.base_map.get(fullkey, '""'))
                lines.append(f"{indent}{key} = {val}")
        return "\n".join(lines)

    def _do_preview(self):
        directory = self.dir_edit.text().strip()
        if not directory or not os.path.isdir(directory):
            QMessageBox.warning(self, "Error", "Please select a valid strings directory.")
            return
        if not self.base_map:
            QMessageBox.warning(self, "Error", "Please select and load a base .rules file.")
            return
        self.tabs.clear(); self.preview_editors.clear()
        for code, cb in self.language_checkboxes.items():
            if not cb.isChecked(): continue
            path = os.path.join(directory, f"{code}.rules")
            target_map = self._parse_target(path)
            content = self._generate_content(target_map)
            editor = QPlainTextEdit(); editor.setPlainText(content)
            editor.setReadOnly(False)
            font = editor.font(); font.setFamily('Consolas'); editor.setFont(font)
            self.tabs.addTab(editor, code)
            self.preview_editors[code] = editor

    def _apply_changes(self):
        directory = self.dir_edit.text().strip()
        if not directory or not os.path.isdir(directory):
            QMessageBox.warning(self, "Error", "Please select a valid strings directory.")
            return
        for code, editor in self.preview_editors.items():
            if not self.language_checkboxes.get(code, True).isChecked(): continue
            text = editor.toPlainText(); out = os.path.join(directory, f"{code}.rules")
            if os.path.isfile(out): shutil.copy(out, out + '.backup')
            try:
                with open(out, 'w', encoding='utf-8') as f: f.write(text)
            except Exception as e:
                QMessageBox.critical(self, "Write failed", f"Could not write {out}: {e}")
        QMessageBox.information(self, "Done", "Selected files updated (backups created).")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if qdarkstyle: app.setStyleSheet(qdarkstyle.load_stylesheet())
    win = RulesLocalizationTool(); win.show(); sys.exit(app.exec())
