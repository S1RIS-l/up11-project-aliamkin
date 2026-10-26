import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QIcon, QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("МирОптики — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
            QLabel {
                color: #000000;
            }
        """)

        central = QWidget()
        layout = QVBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap("resources/logo.png"))
        logo.setScaledContents(False)
        layout.addWidget(logo)
        title = QLabel("Мир Оптики — Каталог")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #70B2AF;")
        layout.addWidget(title)
        central.setLayout(layout)
        self.setCentralWidget(central)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())