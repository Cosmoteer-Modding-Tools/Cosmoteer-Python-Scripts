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
    QTabWidget, QPlainTextEdit, QSplitter,
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt, QTimer

# Attempt to apply a dark style if available
try:
    import qdarkstyle
except ImportError:
    qdarkstyle = None

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

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
        self.preview_lists = {}
        self.preview_line_maps = {}
        self.copy_buttons = {}
        self.selected_keys = {}
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
        line_map = {}
        for token in self.base_tokens:
            ttype = token[0]
            if ttype in ('blank', 'comment', 'section_start', 'section_end'):
                lines.append(token[1])
            else:  # kv
                _, indent, key, fullkey = token
                val = target_map.get(fullkey, self.base_map.get(fullkey, '""'))
                lines.append(f"{indent}{key} = {val}")
                line_map[fullkey] = len(lines) - 1
        return "\n".join(lines), line_map

    def _do_preview(self):
        directory = self.dir_edit.text().strip()
        if not directory or not os.path.isdir(directory):
            QMessageBox.warning(self, "Error", "Please select a valid strings directory.")
            return
        if not self.base_map:
            QMessageBox.warning(self, "Error", "Please select and load a base .rules file.")
            return
        self.tabs.clear(); self.preview_editors.clear()
        self.preview_lists = {}
        self.preview_line_maps = {}
        self.copy_buttons = {}
        self.selected_keys = {}
        for code, cb in self.language_checkboxes.items():
            if not cb.isChecked():
                continue
            path = os.path.join(directory, f"{code}.rules")
            target_map = self._parse_target(path)
            content, line_map = self._generate_content(target_map)
            missing_keys = []
            for token in self.base_tokens:
                if token[0] != "kv":
                    continue
                fullkey = token[3]
                if fullkey not in target_map:
                    missing_keys.append(fullkey)
            editor = QPlainTextEdit()
            editor.setPlainText(content)
            editor.setReadOnly(False)
            font = editor.font()
            font.setFamily("Consolas")
            editor.setFont(font)
            splitter = QSplitter(Qt.Horizontal)
            splitter.setChildrenCollapsible(False)
            splitter.addWidget(editor)
            keys_widget = QWidget()
            keys_widget.setMinimumWidth(220)
            keys_layout = QVBoxLayout(keys_widget)
            keys_layout.setContentsMargins(0, 0, 0, 0)
            header = QLabel(f"New Keys ({len(missing_keys)})")
            header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            keys_layout.addWidget(header)
            keys_list = QListWidget()
            keys_list.setSelectionMode(QListWidget.SingleSelection)
            keys_list.setFocusPolicy(Qt.StrongFocus)
            keys_list.setAlternatingRowColors(True)
            if missing_keys:
                for fullkey in missing_keys:
                    item = QListWidgetItem(fullkey)
                    item.setData(Qt.UserRole, fullkey)
                    keys_list.addItem(item)
                keys_list.setCurrentRow(0)
            else:
                placeholder = QListWidgetItem("No new keys")
                placeholder.setFlags(Qt.NoItemFlags)
                keys_list.addItem(placeholder)
            keys_layout.addWidget(keys_list, 1)
            splitter.addWidget(keys_widget)
            button_panel = QWidget()
            button_panel.setMinimumWidth(90)
            button_layout = QVBoxLayout(button_panel)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.addStretch()
            copy_button = QPushButton("Copy Value")
            copy_button.setEnabled(False)
            copy_button.clicked.connect(lambda _=False, c=code: self._copy_selected_value(c))
            button_layout.addWidget(copy_button)
            button_layout.addStretch()
            splitter.addWidget(button_panel)
            splitter.setStretchFactor(0, 4)
            splitter.setStretchFactor(1, 2)
            splitter.setStretchFactor(2, 0)
            keys_list.currentItemChanged.connect(lambda current, _prev, c=code: self._on_key_selected(c, current))
            self.tabs.addTab(splitter, code)
            self.preview_editors[code] = editor
            self.preview_lists[code] = keys_list
            self.preview_line_maps[code] = line_map
            self.copy_buttons[code] = copy_button
            self.selected_keys[code] = None
            if missing_keys:
                current_item = keys_list.currentItem()
                if current_item is not None:
                    self._on_key_selected(code, current_item)

    def _on_key_selected(self, code, item):
        button = self.copy_buttons.get(code)
        if item is None:
            self.selected_keys[code] = None
            if button:
                button.setEnabled(False)
            return
        key = item.data(Qt.UserRole) if item is not None else None
        if not key:
            self.selected_keys[code] = None
            if button:
                button.setEnabled(False)
            return
        self.selected_keys[code] = key
        if button:
            button.setEnabled(True)
        self._highlight_key(code, key)

    def _highlight_key(self, code, fullkey):
        editor = self.preview_editors.get(code)
        line_map = self.preview_line_maps.get(code, {})
        if not editor or fullkey not in line_map:
            return
        block = editor.document().findBlockByNumber(line_map[fullkey])
        if not block.isValid():
            return
        cursor = editor.textCursor()
        cursor.setPosition(block.position())
        text = block.text()
        eq_index = text.find('=')
        if eq_index == -1:
            cursor.movePosition(QTextCursor.EndOfBlock)
            editor.setTextCursor(cursor)
            editor.centerCursor()
            editor.setFocus()
            return
        value_start = eq_index + 1
        while value_start < len(text) and text[value_start] == ' ':
            value_start += 1
        start_pos = block.position() + value_start
        cursor.setPosition(start_pos)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        editor.setTextCursor(cursor)
        editor.centerCursor()
        editor.setFocus()

    def _copy_selected_value(self, code):
        key = self.selected_keys.get(code)
        if not key:
            return
        editor = self.preview_editors.get(code)
        line_map = self.preview_line_maps.get(code, {})
        if not editor or key not in line_map:
            return
        block = editor.document().findBlockByNumber(line_map[key])
        if not block.isValid():
            return
        text = block.text()
        eq_index = text.find('=')
        if eq_index == -1:
            value = text.strip()
        else:
            value = text[eq_index + 1:].lstrip()
        QApplication.clipboard().setText(value)

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
    if qdarkstyle:
        app.setStyleSheet(qdarkstyle.load_stylesheet())
    win = RulesLocalizationTool()
    win.show()
    if pyi_splash is not None:
        QTimer.singleShot(3500, getattr(pyi_splash, 'close', lambda: None))
    sys.exit(app.exec())
