import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QPushButton, QMessageBox, QComboBox, QLineEdit, QStackedWidget, QDialog, QSpinBox, QFileDialog)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database
from discount import calculate_price


def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100


def create_card(product, on_click=None):
    product_id, name, category, manufacturer, composition, price, image_path, total_quantity = product
    
    card = QWidget()
    card.setObjectName("ProductCard")
    
    if total_quantity == 0:
        card.setStyleSheet("""
            #ProductCard {
                background-color: #ADD8E6;
                border: 2px solid #70B2AF;
            }
            #ProductCard QLabel {
                color: #000000;
                font-family: Calibri;
                border: none;
                background-color: transparent;
            }
        """)
    else:
        card.setStyleSheet("""
            #ProductCard {
                background-color: #FFFFFF;
                border: 2px solid #70B2AF;
            }
            #ProductCard QLabel {
                color: #000000;
                font-family: Calibri;
                border: none;
                background-color: transparent;
            }
        """)
    
    card_layout = QHBoxLayout(card)
    card_layout.setContentsMargins(10, 10, 10, 10)
    card_layout.setSpacing(15)
    
    image_label = QLabel()
    pixmap = QPixmap()
    
    if image_path is not None and os.path.exists(f"resources/Images/{image_path}"):
        pixmap.load(f"resources/Images/{image_path}")
    elif image_path is not None and os.path.exists(image_path):
        pixmap.load(image_path)
    else:
        pixmap.load("resources/picture.png")
        
    image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    image_label.setFixedSize(200, 200)
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
    
    if discount > 15:
        new_price_label.setStyleSheet("color: #2E8B57; font-weight: bold; font-size: 18px;")
    else:
        new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 18px;")
    
    price_layout.addWidget(new_price_label)
    
    if discount <= 0:
        old_price_label.hide()
    
    right_layout.addLayout(price_layout)
    card_layout.addLayout(right_layout)
    
    if on_click:
        card.mousePressEvent = lambda event, pid=product_id: on_click(pid)
    
    return card


class ProductCard(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.db = parent.db if parent is not None else None
        self.product = {}
        self.setWindowTitle("Карточка товара")
        self.resize(400, 600)
        self.setup_ui()
        self.load_product(product_id)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(300)

        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.price_label = QLabel()
        self.price_label.setTextFormat(Qt.RichText)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-size: 14px;")

        self.size_combo = QComboBox()
        self.variant_combo = self.size_combo
        self.size_combo.currentIndexChanged.connect(self.on_variant_changed)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)

        self.add_button = QPushButton("В корзину")
        self.add_button.clicked.connect(self.add_selected_to_cart)

        self.load_image_button = QPushButton("Загрузить изображение")
        self.load_image_button.clicked.connect(self.load_image)

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.price_label)
        layout.addWidget(self.description_label)
        layout.addWidget(QLabel("Вариант:"))
        layout.addWidget(self.size_combo)
        layout.addWidget(QLabel("Количество:"))
        layout.addWidget(self.quantity_spin)
        layout.addWidget(self.add_button)
        layout.addWidget(self.load_image_button)

    def load_product(self, product_id):
        self.product_id = product_id
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, price, description, image_path FROM products WHERE product_id = %s",
                (product_id,)
            )
            product = cursor.fetchone()
            if product is None:
                self.add_button.setEnabled(False)
                QMessageBox.warning(self, "Товар", "Товар не найден")
                return
            name, price, description, image_path = product
            self.product = {"name": name, "price": price}
            self.name_label.setText(name)
            
            old_price = float(price)
            final_price = calculate_price(product_id, old_price)
            if final_price is None:
                final_price = old_price

            discount = calculate_discount(old_price, final_price)

            if discount > 0:
                self.price_label.setText(
                    f"<s style='color:red; font-size:14px; font-weight:normal;'>{old_price:,.0f} ₽</s>  "
                    f"<span style='color:#2E8B57; font-size:18px; font-weight:bold;'>{final_price:,.0f} ₽</span>"
                )
            else:
                self.price_label.setText(f"<span style='font-size:18px;'>{old_price:,.0f} ₽</span>")
            
            formatted_description = description.replace(". ", ".\n") if description else ""
            self.description_label.setText(formatted_description)
            
            if image_path and os.path.exists(f"resources/Images/{image_path}"):
                pixmap = QPixmap(f"resources/Images/{image_path}")
            elif image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
            else:
                pixmap = QPixmap("resources/picture.png")
            self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            cursor.execute(
                "SELECT si.variant_id, v.value, si.quantity FROM stock_items si "
                "JOIN variants v ON si.variant_id = v.variant_id "
                "WHERE si.product_id = %s ORDER BY v.value",
                (product_id,)
            )
            self.size_combo.clear()
            for variant_id, variant_name, quantity in cursor.fetchall():
                self.size_combo.addItem(variant_name, (variant_id, quantity))
            cursor.close()
            self.on_variant_changed()
        finally:
            self.db.release_connection(conn)

    def on_variant_changed(self, index=0):
        selected = self.size_combo.currentData()
        available = max(0, int(selected[1])) if selected else 0
        self.quantity_spin.setRange(1 if available else 0, available)
        self.add_button.setEnabled(available > 0)

    def add_selected_to_cart(self):
        selected = self.size_combo.currentData()
        if not selected or self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Остаток", "Нет доступного остатка")
            return
        QMessageBox.information(
            self, "Этап разработки", "Корзина будет подключена в РТ 19"
        )

    def load_image(self):
        import shutil
        import uuid
        from pathlib import Path
        from PySide6.QtCore import QStandardPaths
        import psycopg

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not file_path:
            return

        if QPixmap(file_path).isNull():
            QMessageBox.warning(self, "Изображение", "Файл не является изображением")
            return

        base = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
        target = Path(base) / "images" / (uuid.uuid4().hex + Path(file_path).suffix)

        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target)

            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET image_path = %s WHERE product_id = %s",
                (str(target), self.product_id)
            )
            if cursor.rowcount != 1:
                raise ValueError("Товар не найден")
            conn.commit()
            cursor.close()

        except (OSError, psycopg.Error, ValueError) as error:
            conn.rollback()
            if target.exists():
                target.unlink()
            QMessageBox.critical(self, "Изображение не сохранено", str(error))
            return
        finally:
            self.db.release_connection(conn)

        self.load_product(self.product_id)


class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None):
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.setWindowTitle("Мир Оптики")
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

    def open_product_card(self, product_id):
        card = ProductCard(product_id, self)
        card.exec()
        self.load_products()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(150, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        
        if self.full_name:
            self.name_label = QLabel(f"ФИО: {self.full_name}")
            self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #000000;")
            header_layout.addWidget(self.name_label)
        
        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #70B2AF;
                color: #000000;
                font-family: Calibri;
                padding: 8px 16px;
                border-radius: 0px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D2F6E7;
            }
        """)
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("background-color: #D2F6E7; border-radius: 0px; padding: 5px;")
        
        main_layout.addWidget(header_widget)

        self.title_label = QLabel("Мир Оптики — Каталог")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #000000;")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.stacked_widget = QStackedWidget()
        
        self.catalog_page = QWidget()
        self.setup_catalog_page()
        self.stacked_widget.addWidget(self.catalog_page)
        
        self.product_page = QWidget()
        product_layout = QVBoxLayout()
        product_layout.addWidget(QLabel("Карточка товара (в разработке)"))
        self.product_page.setLayout(product_layout)
        self.stacked_widget.addWidget(self.product_page)
        
        self.orders_page = QWidget()
        orders_layout = QVBoxLayout()
        orders_layout.addWidget(QLabel("Заказы (в разработке)"))
        self.orders_page.setLayout(orders_layout)
        self.stacked_widget.addWidget(self.orders_page)
        
        self.stacked_widget.setCurrentIndex(0)
        
        main_layout.addWidget(self.stacked_widget)

        self.back_button = QPushButton("Назад")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #70B2AF;
                color: #000000;
                font-family: Calibri;
                padding: 8px 16px;
                border-radius: 0px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D2F6E7;
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        main_layout.addWidget(self.back_button)

        self.setCentralWidget(main_widget)

    def setup_catalog_page(self):
        layout = QVBoxLayout(self.catalog_page)
        
        controls_layout = QHBoxLayout()
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию", "По убыванию"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        controls_layout.addWidget(QLabel("Сортировка:"))
        controls_layout.addWidget(self.sort_combo)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        categories = self.db.get_categories()
        for cat in categories:
            self.filter_combo.addItem(cat[0])
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        controls_layout.addWidget(QLabel("Категория:"))
        controls_layout.addWidget(self.filter_combo)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)
        controls_layout.addWidget(QLabel("Поиск:"))
        controls_layout.addWidget(self.search_input)
        
        layout.addLayout(controls_layout)
        
        buttons_layout = QHBoxLayout()
        
        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        button_style = """
            QPushButton {
                background-color: #70B2AF;
                color: #000000;
                font-family: Calibri;
                padding: 8px 16px;
                border-radius: 0px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D2F6E7;
            }
        """
        self.order_button.setStyleSheet(button_style)
        self.manager_button.setStyleSheet(button_style)
        self.admin_button.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #FFFFFF;")
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setSpacing(15)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        
        for product in self.products:
            card = create_card(product, on_click=self.open_product_card)
            self.list_layout.addWidget(card)
            
        self.list_layout.addStretch()
        
        self.catalog_scroll = QScrollArea()
        self.catalog_scroll.setWidgetResizable(True)
        self.catalog_scroll.setStyleSheet("QScrollArea { border: none; background-color: #FFFFFF;}")
        self.catalog_scroll.setWidget(self.container)
        
        layout.addWidget(self.catalog_scroll)

    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.switch_page(current_index - 1)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        titles = ["Мир Оптики — Каталог", "Мир Оптики — Карточка товара", "Мир Оптики — Заказы"]
        self.title_label.setText(titles[index])
        
        if index == 0:
            self.refresh_catalog()

    def load_products(self):
        search = self.search_input.text().strip()
        category = self.filter_combo.currentText()
        sort = self.sort_combo.currentText()
        
        search_pattern = f"%{search}%"
        
        if sort == "По возрастанию":
            order = "ASC"
        else:
            order = "DESC"
        
        query = f"""
            SELECT 
                p.product_id, 
                p.name, 
                c.name AS category,
                p.manufacturer, 
                p.composition, 
                p.price, 
                p.image_path,
                COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN stock_items si ON p.product_id = si.product_id
            WHERE (p.name ILIKE %s OR p.description ILIKE %s OR p.manufacturer ILIKE %s)
            AND (c.name = %s OR %s = 'Все категории')
            GROUP BY p.product_id, c.name
            ORDER BY p.price {order}
        """
        
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(query, (search_pattern, search_pattern, search_pattern, category, category))
            self.products = cursor.fetchall()
            cursor.close()
        finally:
            self.db.release_connection(conn)
        
        self.refresh_catalog()

    def refresh_catalog(self):
        for i in reversed(range(self.list_layout.count())):
            widget = self.list_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        for product in self.products:
            card = create_card(product, on_click=self.open_product_card)
            self.list_layout.addWidget(card)
            
        self.list_layout.addStretch()

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
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.warning(
            self, "Выход", "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    from login_window import LoginWindow
    
    app = QApplication(sys.argv)
    
    db = Database()
    login_window = LoginWindow(db)
    login_window.show()
    
    exit_code = app.exec()
    db.close_all()
    sys.exit(exit_code)