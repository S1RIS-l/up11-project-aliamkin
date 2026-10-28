import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QPushButton, QMessageBox)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database
from discount import calculate_price
from login_window import LoginWindow

def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100

def create_card(product):
    product_id, name, category, manufacturer, composition, price, image_path, total_quantity = product
    
    card = QWidget()
    card.setObjectName("ProductCard")
    card.setStyleSheet("""
        #ProductCard {
            background-color: #FFFFFF;
            border: 2px solid #70B2AF;
        }
        #ProductCard QLabel {
            color: #000000;
            font-family: Calibri;
            border: none;
        }
    """)
    
    card_layout = QHBoxLayout(card)
    card_layout.setContentsMargins(10, 10, 10, 10)
    card_layout.setSpacing(15)
    
    image_label = QLabel()
    pixmap = QPixmap()
    
    if image_path is not None and os.path.exists(f"resources/Images/{image_path}"):
        pixmap.load(f"resources/Images/{image_path}")
    else:
        pixmap.load("resources/picture.png")
        
    image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    image_label.setFixedSize(100, 100)
    image_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    card_layout.addWidget(image_label)
    
    right_layout = QVBoxLayout()
    right_layout.setSpacing(5)
    
    title_label = QLabel(f"{manufacturer} | {name}")
    title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    right_layout.addWidget(title_label)
    
    category_label = QLabel(f"Категория: {category}")
    category_label.setStyleSheet("font-size: 14px;")
    right_layout.addWidget(category_label)
    
    if total_quantity is not None and total_quantity > 5:
        qty_text = f"Количество: много ({total_quantity})"
        qty_color = "#000000"
        quantity_label = QLabel(qty_text)
        quantity_label.setStyleSheet(f"font-size: 14px; color: {qty_color};")
    else:
        qty_text = f"Количество: мало ({total_quantity})"
        qty_color = "#ff8080"
        quantity_label = QLabel(qty_text)
        quantity_label.setStyleSheet(f"font-size: 14px; color: {qty_color}; font-weight: bold;")
        
    right_layout.addWidget(quantity_label)
    
    composition_label = QLabel(f"Состав: {composition}")
    composition_label.setStyleSheet("font-size: 14px;")
    composition_label.setWordWrap(True)
    right_layout.addWidget(composition_label)
    
    right_layout.addStretch()
    
    price_layout = QHBoxLayout()
    price_layout.addStretch()
    
    old_price = float(price)
    final_price = calculate_price(product_id, old_price)
    if final_price is None:
        final_price = old_price
    
    discount = calculate_discount(old_price, final_price)
    
    old_price_label = QLabel(f"<s>{old_price:,.0f} ₽</s>".replace(',', ' '))
    old_price_label.setStyleSheet("color: red; font-size: 14px;")
    price_layout.addWidget(old_price_label)
    
    new_price_label = QLabel(f"{final_price:,.0f} ₽".replace(',', ' '))
    new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 18px;")
    price_layout.addWidget(new_price_label)
    
    if discount > 0:
        old_price_label.show()
    else:
        old_price_label.hide()
    
    right_layout.addLayout(price_layout)
    card_layout.addLayout(right_layout)
    
    return card

class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None):
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.setWindowTitle("МирОптики")
        self.resize(900, 700)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
        """)
        
        self.db = Database()
        self.products = self.db.get_products()
        
        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(150, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        title_label = QLabel("Мир оптики — Каталог")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #000000;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        if self.full_name:
            self.name_label = QLabel(f"ФИО: {self.full_name}")
            self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #000000;")
            header_layout.addWidget(self.name_label)
        
        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #ff8080;
                color: #000000;
                font-family: Calibri;
                padding: 8px 16px;
                border-radius: 0px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff5050;
            }
        """)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
        
        main_layout.addLayout(header_layout)

        buttons_layout = QHBoxLayout()
        
        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        button_style = """
            QPushButton {
                background-color: #D2F6E7;
                color: #000000;
                font-family: Calibri;
                padding: 8px 16px;
                border-radius: 0px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #70B2AF;
            }
        """
        self.order_button.setStyleSheet(button_style)
        self.manager_button.setStyleSheet(button_style)
        self.admin_button.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)

        container = QWidget()
        container.setStyleSheet("background-color: #FFFFFF;")
        list_layout = QVBoxLayout(container)
        list_layout.setSpacing(15)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        for product in self.products:
            card = create_card(product)
            list_layout.addWidget(card)
            
        list_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF;}")
        scroll.setWidget(container)
        
        main_layout.addWidget(scroll)
        
        self.setCentralWidget(main_widget)

    def setup_role_interface(self):
        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
            self.order_button.hide()
        elif self.role_id == 2:
            self.admin_button.hide()
            self.manager_button.show()
            self.order_button.hide()
        elif self.role_id == 3:
            self.admin_button.hide()
            self.manager_button.hide()
            self.order_button.show()
        else:
            self.order_button.hide()
            self.manager_button.hide()
            self.admin_button.hide()

    def logout(self):
        reply = QMessageBox.question(
            self, "Выход", "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    db = Database()
    login_window = LoginWindow(db)
    login_window.show()
    
    sys.exit(app.exec())