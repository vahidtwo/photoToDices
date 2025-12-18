import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMainWindow, QApplication

from photo_to_dices.art_generator import ArtGenerator

class ConversionWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(str, int)
    error = QtCore.pyqtSignal(str)

    def __init__(self, image_path, scale, dice_width):
        super().__init__()
        self.image_path = image_path
        self.scale = scale
        self.dice_width = dice_width
        self.art_generator = ArtGenerator()

    def run(self):
        try:
            output_path, total_dice = self.art_generator.convert_to_dice_art(
                self.image_path, self.scale, self.dice_width, self.progress.emit
            )
            if output_path:
                self.finished.emit(output_path, total_dice)
            else:
                self.error.emit("Failed to convert image.")
        except Exception as e:
            self.error.emit(str(e))

class DiceArtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo to Dice Art")
        self.setWindowIcon(QtGui.QIcon("icon.png"))  # App icon
        self.setMinimumSize(500, 300)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.init_style()

    def init_ui(self):
        # --- Create Widgets ---
        self.title_label = QtWidgets.QLabel("Photo to Dice Art")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)

        self.file_label = QtWidgets.QLabel("Select an Image:")
        self.file_edit = QtWidgets.QLineEdit()
        self.file_edit.setPlaceholderText("Click 'Browse' to select an image...")
        self.browse_button = QtWidgets.QPushButton("Browse")

        self.options_group = QtWidgets.QGroupBox("Options")
        self.scale_label = QtWidgets.QLabel("Scale Factor:")
        self.scale_spinbox = QtWidgets.QSpinBox()
        self.scale_spinbox.setRange(1, 10)
        self.scale_spinbox.setSuffix("x")

        self.run_button = QtWidgets.QPushButton("Generate Art")
        self.progress_bar = QtWidgets.QProgressBar()
        self.status_bar = self.statusBar()

        # --- Layout ---
        main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        main_layout.addWidget(self.title_label)

        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(self.browse_button)
        main_layout.addLayout(file_layout)

        options_layout = QtWidgets.QFormLayout(self.options_group)
        options_layout.addRow(self.scale_label, self.scale_spinbox)
        main_layout.addWidget(self.options_group)

        main_layout.addWidget(self.run_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addStretch()

        # --- Connections ---
        self.browse_button.clicked.connect(self.browse_for_file)
        self.run_button.clicked.connect(self.run_conversion)

    def init_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 11pt;
            }
            #title_label {
                font-size: 20pt;
                font-weight: bold;
                color: #333;
                padding-bottom: 10px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #a0a0a0;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 11pt;
            }
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px 10px;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
                font-size: 10pt;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 5px;
            }
        """)
        self.title_label.setObjectName("title_label") # For specific styling

    def browse_for_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.file_edit.setText(file_path)

    def run_conversion(self):
        image_path = self.file_edit.text()
        if not Path(image_path).is_file():
            self.show_message("Error", "Please select a valid image file.")
            return

        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Generating your dice art, please wait...")

        self.worker = ConversionWorker(image_path, self.scale_spinbox.value(), 300)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error.connect(self.conversion_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def conversion_finished(self, output_path, total_dice):
        self.run_button.setEnabled(True)
        self.status_bar.showMessage(f"Dice art created with {total_dice} dice!", 5000)
        self.show_message(
            "Success!",
            f"Your amazing dice art has been saved to:\\n{output_path}",
            icon=QMessageBox.Information
        )
        self.reset_ui()

    def conversion_error(self, error_message):
        self.run_button.setEnabled(True)
        self.status_bar.showMessage("Oops! Something went wrong.", 5000)
        self.show_message("Error", error_message, icon=QMessageBox.Critical)
        
    def reset_ui(self):
        self.file_edit.clear()
        self.scale_spinbox.setValue(1)
        self.progress_bar.setValue(0)

    def show_message(self, title, message, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec_()

def main():
    app = QApplication(sys.argv)
    window = DiceArtApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()