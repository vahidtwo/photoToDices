import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QMainWindow, QApplication, QStyleFactory, # QFileDialog needed for filter string parsing
    QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QSpinBox, QProgressBar, QGroupBox, QSpacerItem, QSizePolicy, QAction
)

from photo_to_dices.art_generator import ArtGenerator
from photo_to_dices.custom_file_dialog import CustomFileDialog # Import custom dialog

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
        self.setWindowIcon(QtGui.QIcon("icon.png")) # Ensure 'icon.png' exists in project root
        self.setMinimumSize(650, 450)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.apply_dark_style()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Title Section
        title_section = QHBoxLayout()
        icon_label = QLabel()
        pixmap = QtGui.QPixmap("icon.png") # Load icon
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        
        app_title = QLabel("<h1>Photo to Dice Art</h1>")
        app_title.setAlignment(QtCore.Qt.AlignCenter)
        
        title_section.addStretch()
        title_section.addWidget(icon_label)
        title_section.addWidget(app_title)
        title_section.addStretch()
        main_layout.addLayout(title_section)

        # File Selection Group
        file_group = QGroupBox("Input Image")
        file_layout = QFormLayout(file_group)
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select an image file...")
        self.file_input.setReadOnly(True)
        
        browse_action = QAction(self)
        browse_action.setIcon(QtGui.QIcon.fromTheme("document-open")) # Use a system icon
        browse_action.triggered.connect(self.browse_for_file)
        self.file_input.addAction(browse_action, QLineEdit.TrailingPosition)
        
        file_layout.addRow("Image Path:", self.file_input)
        main_layout.addWidget(file_group)

        # Options Group
        options_group = QGroupBox("Conversion Settings")
        options_layout = QFormLayout(options_group)
        self.scale_spinbox = QSpinBox()
        self.scale_spinbox.setRange(1, 10)
        self.scale_spinbox.setValue(1)
        self.scale_spinbox.setSuffix("x")
        self.scale_spinbox.setToolTip("Sets the scaling factor for the output dice art.")
        options_layout.addRow("Output Scale:", self.scale_spinbox)
        main_layout.addWidget(options_group)

        # Action Button
        self.generate_button = QPushButton("✨ Generate Dice Art")
        self.generate_button.setFixedHeight(55)
        main_layout.addWidget(self.generate_button)

        # Progress & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to convert!")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Connections
        self.generate_button.clicked.connect(self.start_conversion)
        
        # Initial state
        self.reset_ui_state()

    def apply_dark_style(self):
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50; /* Deep blue-gray */
                color: #ecf0f1; /* Light gray text */
            }
            QWidget {
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 10pt;
                color: #ecf0f1;
            }
            h1 {
                color: #3498db; /* Bright blue accent */
                font-size: 24pt;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QGroupBox {
                background-color: #34495e; /* Slightly lighter blue-gray for groups */
                border: 1px solid #3498db; /* Accent border */
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 25px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center; /* Center title */
                padding: 0 10px;
                color: #3498db;
                font-size: 12pt;
                font-weight: bold;
            }
            QLineEdit, QSpinBox {
                background-color: #4a6480; /* Darker input fields */
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 8px;
            }
            QLineEdit:read-only {
                background-color: #4a6480;
                color: #bdc3c7; /* Muted text for read-only */
            }
            QPushButton {
                background-color: #3498db; /* Primary accent */
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 12pt;
                font-weight: bold;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #2980b9; /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #2471a3; /* Even darker on press */
            }
            QPushButton:disabled {
                background-color: #7f8c8d; /* Greyed out for disabled */
                color: #bdc3c7;
            }
            QProgressBar {
                border: 1px solid #3498db;
                border-radius: 7px;
                background-color: #4a6480;
                text-align: center;
                color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
            QLabel#status_label { /* Targeting status label specifically */
                font-size: 10pt;
                color: #bdc3c7;
                margin-top: 10px;
            }
            QMessageBox {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QMessageBox QLabel {
                color: #ecf0f1;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.status_label.setObjectName("status_label") # for specific styling

    def browse_for_file(self):
        initial_path = self.file_input.text() if self.file_input.text() else str(Path.home())
        dialog = CustomFileDialog(self, initial_path=initial_path, file_filter="*.png *.jpg *.jpeg *.bmp *.gif")
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_file = dialog.get_selected_file()
            if selected_file:
                self.file_input.setText(selected_file)

    def start_conversion(self):
        image_path = self.file_input.text()
        if not Path(image_path).is_file():
            self.show_message("Input Error", "Please select a valid image file before generating art.", QMessageBox.Warning)
            return

        self.set_ui_enabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Generating your dice art... This might take a moment.")

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
        self.status_label.setText(f"Dice art generated! Used {total_dice} dice.")
        self.show_message(
            "Conversion Complete",
            f"Your awesome dice art has been saved to:\n{output_path}",
            QMessageBox.Information
        )
        self.reset_ui_state()

    def conversion_error(self, error_message):
        self.set_ui_enabled(True)
        self.status_label.setText("Conversion failed!")
        self.show_message("Conversion Error", f"An error occurred: {error_message}", QMessageBox.Critical)

    def set_ui_enabled(self, enabled):
        self.file_input.setEnabled(enabled)
        # self.browse_button is integrated into file_input as an action
        self.scale_spinbox.setEnabled(enabled)
        self.generate_button.setEnabled(enabled)

    def reset_ui_state(self):
        self.file_input.clear()
        self.scale_spinbox.setValue(1)
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready to convert!")

    def show_message(self, title, message, icon=QMessageBox.Information):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        # Apply custom stylesheet for message box
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QMessageBox QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        msg_box.exec_()

def main():
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    app = QApplication(sys.argv)
    window = DiceArtApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()