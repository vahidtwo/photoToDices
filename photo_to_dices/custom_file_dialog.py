from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QStyle,
)


class CustomFileDialog(QDialog):
    def __init__(self, parent=None, initial_path=None, file_filter="*"):
        super().__init__(parent)
        self.setWindowTitle("Select Image File")
        self.setMinimumSize(600, 400)
        self.selected_file = None
        self.file_filter = file_filter.split()  # e.g., ["*.png", "*.jpg"]

        self.current_path = Path(initial_path) if initial_path else Path.home()
        if not self.current_path.is_dir():
            self.current_path = self.current_path.parent

        self.init_ui()
        self.load_directory_contents()
        self.apply_style()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Path display and navigation
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(str(self.current_path))
        self.path_edit.setReadOnly(True)

        self.up_button = QPushButton()
        self.up_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.up_button.setFixedSize(30, 30)
        self.up_button.clicked.connect(self.navigate_up)

        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.up_button)
        main_layout.addLayout(path_layout)

        # File/Directory List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.handle_item_double_click)
        main_layout.addWidget(self.list_widget)

        # Action buttons
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

    def apply_style(self):
        # Apply a similar dark theme to the dialog itself
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 10pt;
            }
            QLineEdit {
                background-color: #4a6480;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#up_button { /* Specific style for up button if needed */
                padding: 5px;
            }
            QListWidget {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 3px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

    def load_directory_contents(self):
        self.list_widget.clear()
        self.path_edit.setText(str(self.current_path))

        # Add parent directory
        if self.current_path.parent != self.current_path:  # Avoid infinite 'up' from root
            item = QListWidgetItem("..")
            item.setData(QtCore.Qt.UserRole, self.current_path.parent)
            self.list_widget.addItem(item)

        for entry in sorted(self.current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            item_text = entry.name
            if entry.is_dir():
                item_text += "/"
                item.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
            elif self._is_file_match(entry):
                item.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
            else:
                continue  # Skip files that don't match the filter

            item = QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, entry)  # Store the full Path object
            self.list_widget.addItem(item)

    def _is_file_match(self, file_path):
        if not self.file_filter or file_path.is_dir():
            return True
        for pattern in self.file_filter:
            if file_path.match(pattern):
                return True
        return False

    def navigate_up(self):
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
            self.load_directory_contents()

    def handle_item_double_click(self, item):
        path_obj = item.data(QtCore.Qt.UserRole)
        if path_obj.is_dir():
            self.current_path = path_obj
            self.load_directory_contents()
        else:
            self.selected_file = str(path_obj)
            self.accept()

    def get_selected_file(self):
        return self.selected_file
