import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMainWindow, QApplication, QStyleFactory

from photo_to_dices.art_generator import ArtGenerator

class ConversionWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal(str, int)
    error = QtCore.pyqtSignal(str)

    def __init__(self, image_path, scale):
        super().__init__()
        self.image_path = image_path
        self.scale = scale
        self.art_generator = ArtGenerator()

    def run(self):
        try:
            # DEFAULT_DICE_WIDTH from ArtGenerator is used here
            output_path, total_dice = self.art_generator.convert_to_dice_art(
                self.image_path, self.scale, self.art_generator.DEFAULT_DICE_WIDTH, self.progress.emit
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
        self.setWindowTitle("Photo to Dice Art Generator")
        self.setWindowIcon(QtGui.QIcon("icon.png")) # Ensure 'icon.png' exists
        self.setMinimumSize(600, 400)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.apply_dark_style()
        
    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Title
        title_label = QtWidgets.QLabel("<h1>🎲 Photo to Dice Art 🖼️</h1>")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # File selection
        file_selection_group = QtWidgets.QGroupBox("Image Selection")
        file_layout = QtWidgets.QHBoxLayout(file_selection_group)
        self.file_input = QtWidgets.QLineEdit()
        self.file_input.setPlaceholderText("No image selected...")
        self.file_input.setReadOnly(True)
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.browse_button.setIcon(QtGui.QIcon.fromTheme("folder-open")) # System icon
        
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.browse_button)
        main_layout.addWidget(file_selection_group)

        # Options
        options_group = QtWidgets.QGroupBox("Conversion Options")
        options_layout = QtWidgets.QFormLayout(options_group)
        
        self.scale_label = QtWidgets.QLabel("Output Scale Factor:")
        self.scale_spinbox = QtWidgets.QSpinBox()
        self.scale_spinbox.setRange(1, 10)
        self.scale_spinbox.setValue(1)
        self.scale_spinbox.setSuffix("x")
        self.scale_spinbox.setToolTip("Scales the output image size relative to the input.")
        
        options_layout.addRow(self.scale_label, self.scale_spinbox)
        main_layout.addWidget(options_group)

        # Action Button
        self.generate_button = QtWidgets.QPushButton("✨ Generate Dice Art ✨")
        self.generate_button.setFixedHeight(50)
        main_layout.addWidget(self.generate_button)

        # Progress Bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        main_layout.addStretch() # Pushes everything to the top

        # Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready to convert!", 0)

        # Connections
        self.browse_button.clicked.connect(self.browse_for_file)
        self.generate_button.clicked.connect(self.start_conversion)

    def apply_dark_style(self):
        # Set a dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                font-size: 10pt;
            }
            h1 {
                color: #a8dadc;
            }
            QGroupBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                color: #f0f0f0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: #a8dadc;
                font-size: 11pt;
                font-weight: bold;
            }
            QLineEdit, QSpinBox {
                background-color: #4c4c4c;
                color: #f0f0f0;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 6px;
            }
            QLineEdit:read-only {
                background-color: #3a3a3a;
                color: #b0b0b0;
            }
            QPushButton {
                background-color: #a8dadc; /* Accent color */
                color: #2b2b2b;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 11pt;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #8bb7b9; /* Darker accent on hover */
            }
            QPushButton:pressed {
                background-color: #6a9799; /* Even darker on press */
            }
            QPushButton:disabled {
                background-color: #555;
                color: #999;
            }
            QProgressBar {
                border: 1px solid #a8dadc;
                border-radius: 7px;
                background-color: #4c4c4c;
                text-align: center;
                color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #a8dadc;
                border-radius: 6px;
            }
            QStatusBar {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border-top: 1px solid #555;
            }
        """)

    def browse_for_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.file_input.setText(file_path)

    def start_conversion(self):
        image_path = self.file_input.text()
        if not Path(image_path).is_file():
            self.show_message("Error", "Please select a valid image file before generating art.", QMessageBox.Critical)
            return

        self.set_ui_enabled(False)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Generating your dice art... This might take a moment.", 0)

        self.worker = ConversionWorker(image_path, self.scale_spinbox.value())
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error.connect(self.conversion_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def conversion_finished(self, output_path, total_dice):
        self.set_ui_enabled(True)
        self.progress_bar.setValue(100)
        self.status_bar.showMessage(f"Dice art generated! Used {total_dice} dice.", 5000)
        self.show_message(
            "Conversion Complete",
            f"Your awesome dice art has been saved to:\n{output_path}",
            QMessageBox.Information
        )
        self.reset_ui_state()

    def conversion_error(self, error_message):
        self.set_ui_enabled(True)
        self.status_bar.showMessage("Conversion failed!", 5000)
        self.show_message("Conversion Error", f"An error occurred: {error_message}", QMessageBox.Critical)

    def set_ui_enabled(self, enabled):
        self.file_input.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.scale_spinbox.setEnabled(enabled)
        self.generate_button.setEnabled(enabled)

    def reset_ui_state(self):
        self.file_input.clear()
        self.scale_spinbox.setValue(1)
        self.progress_bar.setValue(0)
        self.status_bar.clearMessage()
        self.status_bar.showMessage("Ready to convert!", 0)

    def show_message(self, title, message, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QMessageBox QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        msg_box.exec_()

def main():
    # Set Fusion style for a more modern base look across platforms
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    app = QApplication(sys.argv)
    window = DiceArtApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()