#!/usr/bin/env python3
import sys
import os
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QScrollArea, QGridLayout,
    QLineEdit, QHBoxLayout, QComboBox, QMessageBox,
    QSpinBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ImageEntry(QWidget):
    def __init__(self, image_path, thumb_size=128, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        layout = QVBoxLayout()

        # Thumbnail display
        self.thumbnail_label = QLabel()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(
            thumb_size, thumb_size,
            Qt.KeepAspectRatio, Qt.FastTransformation
        )
        self.thumbnail_label.setPixmap(pixmap)
        layout.addWidget(self.thumbnail_label)

        # Caption entry
        self.caption_edit = QLineEdit()
        self.caption_edit.setPlaceholderText("Enter caption for LoRA training...")
        layout.addWidget(self.caption_edit)

        self.setLayout(layout)

    def get_caption(self):
        return self.caption_edit.text().strip()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Art LoRA Dataset Preprocessor")
        self.input_folder = None
        self.output_folder = None
        
        self.init_ui()
        self.entries = []  # [(ImageEntry, filename), ...]

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Folder selectors
        folder_layout = QHBoxLayout()
        self.input_btn = QPushButton("Select Input Folder")
        self.input_btn.clicked.connect(self.select_input_folder)
        folder_layout.addWidget(self.input_btn)

        self.output_btn = QPushButton("Select Output Folder")
        self.output_btn.clicked.connect(self.select_output_folder)
        folder_layout.addWidget(self.output_btn)

        main_layout.addLayout(folder_layout)

        # Target resolution & background settings
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Target Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(64, 2048)
        self.width_spin.setSingleStep(64)
        self.width_spin.setValue(512)
        res_layout.addWidget(self.width_spin)

        res_layout.addWidget(QLabel("Target Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(64, 2048)
        self.height_spin.setSingleStep(64)
        self.height_spin.setValue(512)
        res_layout.addWidget(self.height_spin)

        res_layout.addWidget(QLabel("Background:"))
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(["white", "black"])
        res_layout.addWidget(self.bg_combo)

        main_layout.addLayout(res_layout)

        # Scrollable thumbnail grid
        self.scroll = QScrollArea()
        self.thumb_widget = QWidget()
        self.thumb_layout = QGridLayout()
        self.thumb_widget.setLayout(self.thumb_layout)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.thumb_widget)
        main_layout.addWidget(self.scroll)

        # Process button
        self.process_btn = QPushButton("Process and Save Dataset")
        self.process_btn.clicked.connect(self.process_images)
        main_layout.addWidget(self.process_btn)

        self.setLayout(main_layout)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_folder = folder
            self.load_images()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder

    def load_images(self):
        # Clear existing
        for i in reversed(range(self.thumb_layout.count())):
            w = self.thumb_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.entries.clear()

        # List image files
        exts = ('.png', '.jpg', '.jpeg')
        files = [f for f in os.listdir(self.input_folder)
                 if f.lower().endswith(exts)]

        # Add entries
        for idx, fname in enumerate(files):
            path = os.path.join(self.input_folder, fname)
            entry = ImageEntry(path)
            self.entries.append((entry, fname))
            row, col = divmod(idx, 4)
            self.thumb_layout.addWidget(entry, row, col)

        self.thumb_widget.adjustSize()

    def process_images(self):
        # Validate folders
        if not self.input_folder or not self.output_folder:
            QMessageBox.warning(self, "Error",
                                "Please select both input and output folders.")
            return

        target_w = self.width_spin.value()
        target_h = self.height_spin.value()
        bg_color = self.bg_combo.currentText()

        # Ensure captions filled
        for entry, fname in self.entries:
            if not entry.get_caption():
                QMessageBox.warning(
                    self, "Missing Caption",
                    f"No caption entered for {fname}"
                )
                return

        # Process each image
        for entry, fname in self.entries:
            img = Image.open(entry.image_path)

            # Flatten transparency
            if img.mode in ("RGBA", "LA"):
                alpha = img.split()[-1]
                bg = Image.new("RGBA", img.size, (255,255,255,255))
                bg.paste(img, mask=alpha)
                img = bg.convert("RGB")
            else:
                img = img.convert("RGB")

            orig_w, orig_h = img.size
            scale = min(target_w/orig_w, target_h/orig_h)
            new_w = max(1, int(orig_w * scale))
            new_h = max(1, int(orig_h * scale))

            # Resize with nearest neighbor
            up = img.resize((new_w, new_h), Image.NEAREST)

            # Center on canvas
            canvas = Image.new("RGB", (target_w, target_h), bg_color)
            x = (target_w - new_w) // 2
            y = (target_h - new_h) // 2
            canvas.paste(up, (x, y))

            # Save image
            out_img_path = os.path.join(self.output_folder, fname)
            canvas.save(out_img_path)

            # Save caption file
            base, _ = os.path.splitext(fname)
            txt_path = os.path.join(self.output_folder, f"{base}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(entry.get_caption())

        QMessageBox.information(self, "Done", "Dataset generated successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
