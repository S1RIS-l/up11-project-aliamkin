from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide6.QtGui import QIcon
import os

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.main_window = None
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        
        if os.path.exists("resources/icon.ico"):
            self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
            QLabel {
                color: #000000;
                font-size: 14px;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #70B2AF;
                border-radius: 0px;
            }
            QPushButton {
                font-size: 14px;
                padding: 8px;
                background-color: #70B2AF;
                color: #000000;
                border: 1px solid #000000;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #D2F6E7;
            }
        """)
        
        layout = QVBoxLayout()
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)
        
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_button)
        
        self.setLayout(layout)

    def check_login(self):
        login = self.login_input.text().strip()
        
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return
        
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, role_id, last_name, first_name, middle_name FROM users WHERE login = %s",
                (login,)
            )
            result = cursor.fetchone()
            cursor.close()
            
            if result is None:
                QMessageBox.warning(self, "Ошибка", "Неверный логин")
            else:
                self.user_id = result[0]
                self.role_id = result[1]
                last_name = result[2]
                first_name = result[3]
                middle_name = result[4] if result[4] else ""
                self.full_name = f"{last_name} {first_name} {middle_name}".strip()
                self.open_main_window()
        finally:
            self.db.release_connection(conn)
    
    def open_main_window(self):
        from main import MainWindow
        self.main_window = MainWindow(role_id=self.role_id, full_name=self.full_name)
        self.main_window.show()
        self.close()

    
    def closeEvent(self, event):
        if self.main_window is None:
            from main import MainWindow
            self.main_window = MainWindow(role_id=None, full_name="Гость")
            self.main_window.show()
        event.accept()