import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database

def create_card(product):
    product_id, name, category, manufacturer, composition, price, image_path, total_quantity = product
    
    card = QWidget()
    card.setStyleSheet("""
        QWidget {
            background-color: #FFFFFF;
        }
        QLabel {
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
    
    if image_path:
        pixmap.load(f"resources/{image_path}")
    
    if pixmap.isNull():
        pixmap.load("resources/picture.png")
        
    image_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    image_label.setFixedSize(120, 120)
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
    
    if total_quantity > 5:
        qty_text = f"Количество: много ({total_quantity})"
        qty_color = "#000000"
    elif total_quantity > 0:
        qty_text = f"Количество: мало ({total_quantity})"
        qty_color = "#ff8080"
    else:
        qty_text = "Нет в наличии"
        qty_color = "#ff8080"
        
    quantity_label = QLabel(qty_text)
    quantity_label.setStyleSheet(f"font-size: 14px; color: {qty_color};")
    right_layout.addWidget(quantity_label)
    
    composition_label = QLabel(f"Состав: {composition}")
    composition_label.setStyleSheet("font-size: 14px;")
    composition_label.setWordWrap(True)
    right_layout.addWidget(composition_label)
    
    right_layout.addStretch()
    
    price_layout = QHBoxLayout()
    price_layout.addStretch()
    price_label = QLabel(f"{price:,.0f} руб.".replace(',', ' '))
    price_label.setStyleSheet("font-size: 18px; font-weight: bold;")
    price_layout.addWidget(price_label)
    
    right_layout.addLayout(price_layout)
    card_layout.addLayout(right_layout)
    
    return card

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("МирОптики — Каталог")
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
        
        container = QWidget()
        list_layout = QVBoxLayout(container)
        list_layout.setSpacing(15)
        list_layout.setContentsMargins(15, 15, 15, 15)
        
        for product in self.products:
            card = create_card(product)
            list_layout.addWidget(card)
            
        list_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setWidget(container)
        
        self.setCentralWidget(scroll)
    
    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())