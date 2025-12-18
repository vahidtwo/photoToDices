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
                self.image_path, self.scale
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
        self.setWindowIcon(QtGui.QIcon.fromTheme("app-icon"))  # Placeholder for app icon

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.init_style()

    def init_ui(self):
        # --- Create Widgets ---
        self.file_label = QtWidgets.QLabel("Image File:")
        self.file_edit = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse...")
        self.browse_button.setIcon(QtGui.QIcon.fromTheme("document-open"))

        self.scale_label = QtWidgets.QLabel("Scale Factor:")
        self.scale_spinbox = QtWidgets.QSpinBox()
        self.scale_spinbox.setRange(1, 10)
        self.scale_spinbox.setSuffix("x")

        self.run_button = QtWidgets.QPushButton("Generate Dice Art")
        self.run_button.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))

        self.progress_bar = QtWidgets.QProgressBar()
        self.status_bar = self.statusBar()

        # --- Layout ---
        layout = QtWidgets.QGridLayout(self.central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.file_label, 0, 0)
        layout.addWidget(self.file_edit, 0, 1)
        layout.addWidget(self.browse_button, 0, 2)

        layout.addWidget(self.scale_label, 1, 0)
        layout.addWidget(self.scale_spinbox, 1, 1)

        layout.addWidget(self.run_button, 2, 0, 1, 3)
        layout.addWidget(self.progress_bar, 3, 0, 1, 3)

        # --- Connections ---
        self.browse_button.clicked.connect(self.browse_for_file)
        self.run_button.clicked.connect(self.run_conversion)

    def init_style(self):
        self.setStyleSheet("""
            QWidget {
                font-size: 11pt;
            }
            QPushButton {
                background-color: #4CAF50; /* Green */
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 12pt;
                margin: 4px 2px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QLabel {
                font-weight: bold;
            }
        """)

    def browse_for_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if file_path:
            self.file_edit.setText(file_path)

    def run_conversion(self):
        image_path = self.file_edit.text()
        if not Path(image_path).is_file():
            self.show_error("Please select a valid image file.")
            return

        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Conversion in progress...")

        self.worker = ConversionWorker(image_path, self.scale_spinbox.value(), 300)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error.connect(self.conversion_error)
        self.worker.start()

    def conversion_finished(self, output_path, total_dice):
        self.run_button.setEnabled(True)
        self.progress_bar.setValue(100)
        self.status_bar.showMessage(f"Successfully created dice art with {total_dice} dice.", 5000)

        reply = QMessageBox.information(
            self,
            "Conversion Complete",
            f"Dice art saved to:\n{output_path}",
            QMessageBox.Ok
        )
        if reply == QMessageBox.Ok:
            self.reset_ui()
            
    def reset_ui(self):
        self.file_edit.clear()
        self.scale_spinbox.setValue(1)
        self.progress_bar.setValue(0)


    def conversion_error(self, error_message):
        self.run_button.setEnabled(True)
        self.status_bar.showMessage("Conversion failed.", 5000)
        self.show_error(error_message)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

def main():
    app = QApplication(sys.argv)
    window = DiceArtApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()