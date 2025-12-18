import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
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
                self.image_path, self.scale, self.dice_width
            )
            if output_path:
                self.finished.emit(output_path, total_dice)
            else:
                self.error.emit("Failed to convert image.")
        except Exception as e:
            self.error.emit(str(e))

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(400, 250)
        MainWindow.setWindowTitle("PHOTO TO DICE")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.create_widgets()
        self.layout_widgets()
        self.connect_widgets()

        MainWindow.setCentralWidget(self.centralwidget)

    def create_widgets(self):
        self.Browse = QtWidgets.QPushButton("Browse")
        self.run = QtWidgets.QPushButton("Run")
        self.edt_file = QtWidgets.QLineEdit()
        self.edt_scale = QtWidgets.QLineEdit()
        self.label_2 = QtWidgets.QLabel("File:")
        self.label_3 = QtWidgets.QLabel("total dice:")
        self.label_11 = QtWidgets.QLabel("scale:")
        self.total_dice = QtWidgets.QLabel("0")
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)

    def layout_widgets(self):
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        
        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(self.label_2)
        file_layout.addWidget(self.edt_file)
        file_layout.addWidget(self.Browse)
        
        scale_layout = QtWidgets.QHBoxLayout()
        scale_layout.addWidget(self.label_11)
        scale_layout.addWidget(self.edt_scale)
        
        main_layout.addLayout(file_layout)
        main_layout.addLayout(scale_layout)
        main_layout.addWidget(self.run)
        main_layout.addWidget(self.progressBar)
        
        total_layout = QtWidgets.QHBoxLayout()
        total_layout.addWidget(self.label_3)
        total_layout.addWidget(self.total_dice)
        main_layout.addLayout(total_layout)

    def connect_widgets(self):
        self.Browse.clicked.connect(self.get_file)
        self.run.clicked.connect(self.convert)

    def get_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            None, "QFileDialog.getOpenFileName()", "", "All Files (*);;Python Files (*.py)", options=options
        )
        if fileName:
            self.edt_file.setText(fileName)

    def convert(self):
        image_path = self.edt_file.text()
        if not Path(image_path).is_file():
            self.show_error("Please select a valid image file.")
            return

        try:
            scale = int(self.edt_scale.text()) if self.edt_scale.text() else 1
            if scale <= 0:
                scale = 1
        except ValueError:
            self.show_error("Invalid scale value. Please enter a number.")
            return

        self.run.setEnabled(False)
        self.progressBar.setValue(0)

        self.worker = ConversionWorker(image_path, scale, 300)
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error.connect(self.conversion_error)
        self.worker.start()

    def conversion_finished(self, output_path, total_dice):
        self.run.setEnabled(True)
        self.progressBar.setValue(100)
        self.total_dice.setText(str(total_dice))
        
        reply = QMessageBox.question(
            None,
            "Conversion Finished",
            f"Image saved to {output_path}\nDo you want to convert another image?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.No:
            sys.exit(0)
        else:
            self.edt_file.clear()
            self.edt_scale.clear()
            self.progressBar.setValue(0)
            self.total_dice.setText("0")


    def conversion_error(self, error_message):
        self.run.setEnabled(True)
        self.show_error(error_message)

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()