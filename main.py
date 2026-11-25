#Комментарий
import sys
import os
from decimal import Decimal
from datetime import date
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                               QWidget, QScrollArea, QHBoxLayout, QPushButton, 
                               QMessageBox, QComboBox, QLineEdit, QStackedWidget,
                               QDialog, QSpinBox, QFileDialog, QTableWidget, QTableWidgetItem,
                               QInputDialog, QAbstractItemView, QDateEdit)
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
    
    composition_label = QLabel(f"Состав: {composition or 'Не указан'}")
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
        self.main_window = parent
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

        

        self.delete_button = QPushButton("Удалить")
        self.delete_button.setStyleSheet("""
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
        self.delete_button.clicked.connect(self.delete_product)

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
        layout.addWidget(self.delete_button)

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
        variant_id, available = selected
        if self.main_window is not None and hasattr(self.main_window, "add_to_cart"):
            self.main_window.add_to_cart(
                self.product_id, variant_id, self.product["name"],
                self.quantity_spin.value(), self.product["price"]
            )
        self.close()

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

    def delete_product(self):
        import psycopg

        reply = QMessageBox.question(
            self, "Удаление", "Вы уверены, что хотите удалить товар?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM products WHERE product_id = %s",
                (self.product_id,)
            )
            conn.commit()
            cursor.close()

            QMessageBox.information(self, "Успех", "Товар удалён")
            if self.main_window is not None and hasattr(self.main_window, "load_products"):
                self.main_window.load_products()
            self.close()

        except psycopg.errors.ForeignKeyViolation:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", "Товар нельзя удалить: он есть в заказах")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")
        finally:
            self.db.release_connection(conn)


class AddOrderDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.order_id = None
        self.selected_product_id = None
        self.selected_price = 0
        self.setWindowTitle("Добавить заказ")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Клиент:"))
        self.client_combo = QComboBox()
        conn = self.db.get_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, CONCAT_WS(' ', last_name, first_name) FROM users WHERE role_id = 3")
                for user in cursor.fetchall():
                    self.client_combo.addItem(user[1], user[0])
                cursor.close()
            finally:
                self.db.release_connection(conn)
        layout.addWidget(self.client_combo)

        layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Завершён"])
        self.status_combo.setCurrentIndex(0)
        layout.addWidget(self.status_combo)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_order)
        layout.addWidget(self.save_button)

        layout.addWidget(QLabel("Поиск товара:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)
        layout.addWidget(self.search_input)

        self.products_combo = QComboBox()
        self.products_combo.currentIndexChanged.connect(self.on_product_changed)
        layout.addWidget(self.products_combo)

        layout.addWidget(QLabel("Вариант:"))
        self.variant_combo = QComboBox()
        self.variant_combo.currentIndexChanged.connect(self.on_variant_changed)
        layout.addWidget(self.variant_combo)

        layout.addWidget(QLabel("Количество:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10)
        layout.addWidget(self.quantity_spin)

        self.add_item_button = QPushButton("Добавить в заказ")
        self.add_item_button.clicked.connect(lambda: self.add_item_to_order(self.order_id))
        layout.addWidget(self.add_item_button)

        self.cancel_button = QPushButton("Закрыть")
        self.cancel_button.clicked.connect(self.accept)
        layout.addWidget(self.cancel_button)

        self.load_products()

    def save_order(self):
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        try:
            cursor = conn.cursor()
            user_id = self.client_combo.currentData()
            status = self.status_combo.currentText()

            cursor.execute(
                "INSERT INTO orders (order_date, user_id, status) VALUES (%s, %s, %s) RETURNING order_id",
                (date.today(), user_id, status)
            )
            self.order_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", f"Заказ № {self.order_id} создан")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)

    def load_products(self):
        search = self.search_input.text().strip()
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.product_id, p.name, p.price
                FROM products p
                WHERE p.name ILIKE %s
            """, (f"%{search}%",))
            products = cursor.fetchall()
            cursor.close()

            self.products_combo.clear()
            for product in products:
                self.products_combo.addItem(f"{product[1]} ({product[2]} ₽)", (product[0], product[2]))
        finally:
            self.db.release_connection(conn)

    def on_product_changed(self):
        data = self.products_combo.currentData()
        if not data:
            self.selected_product_id = None
            self.selected_price = 0
            self.variant_combo.clear()
            return
        self.selected_product_id, self.selected_price = data
        self.load_variants(self.selected_product_id)

    def load_variants(self, product_id):
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT si.variant_id, v.value, si.quantity
                FROM stock_items si
                JOIN variants v ON si.variant_id = v.variant_id
                WHERE si.product_id = %s
                ORDER BY v.value
            """, (product_id,))
            variants = cursor.fetchall()
            cursor.close()

            self.variant_combo.blockSignals(True)
            self.variant_combo.clear()
            for variant_id, value, stock in variants:
                self.variant_combo.addItem(f"{value} (остаток: {stock})", (variant_id, stock))
            self.variant_combo.blockSignals(False)
            self.on_variant_changed()
        finally:
            self.db.release_connection(conn)

    def on_variant_changed(self):
        selected = self.variant_combo.currentData()
        stock = max(0, int(selected[1])) if selected else 0
        self.quantity_spin.setRange(1 if stock > 0 else 0, stock)
        self.add_item_button.setEnabled(stock > 0)

    def add_item_to_order(self, order_id):
        if not order_id:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте заказ")
            return

        selected_variant = self.variant_combo.currentData()
        if not selected_variant or self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Выберите доступный вариант товара")
            return

        variant_id, _ = selected_variant
        product_id = self.selected_product_id
        quantity = self.quantity_spin.value()
        price = self.selected_price

        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                (order_id, product_id, variant_id, quantity, price)
            )
            cursor.execute(
                "UPDATE stock_items SET quantity = quantity - %s WHERE product_id = %s AND variant_id = %s",
                (quantity, product_id, variant_id)
            )
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", "Товар добавлен в заказ")
            self.load_variants(product_id)
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)

class EditOrderDialog(QDialog):
    def __init__(self, db, order_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.order_id = order_id
        self.setWindowTitle("Редактировать заказ")
        self.setup_ui()
        self.load_order_data()
        self.load_order_details(self.order_id)
        self.load_total(self.order_id)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Дата заказа:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        layout.addWidget(self.date_edit)

        self.save_date_button = QPushButton("Сохранить дату")
        self.save_date_button.clicked.connect(self.save_date)
        layout.addWidget(self.save_date_button)

        layout.addWidget(QLabel("Клиент:"))
        self.client_combo = QComboBox()
        conn = self.db.get_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, CONCAT_WS(' ', last_name, first_name) FROM users WHERE role_id = 3")
                for user in cursor.fetchall():
                    self.client_combo.addItem(user[1], user[0])
                cursor.close()
            finally:
                self.db.release_connection(conn)
        layout.addWidget(self.client_combo)

        layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Завершён"])
        layout.addWidget(self.status_combo)

        layout.addWidget(QLabel("Состав заказа:"))
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels(["Товар", "Количество", "Цена", "Сумма"])
        layout.addWidget(self.details_table)

        self.total_label = QLabel("Итого: 0 ₽")
        layout.addWidget(self.total_label)

        self.remove_item_button = QPushButton("Удалить позицию")
        self.remove_item_button.clicked.connect(self.on_remove_item_clicked)
        layout.addWidget(self.remove_item_button)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_order)
        layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

    def load_order_data(self):
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT order_date, user_id, status FROM orders WHERE order_id = %s", (self.order_id,))
            order = cursor.fetchone()
            cursor.close()

            if order is None:
                QMessageBox.critical(self, "Ошибка", "Заказ не найден")
                self.reject()
                return

            self.date_edit.setDate(order[0])

            index = self.client_combo.findData(order[1])
            if index >= 0:
                self.client_combo.setCurrentIndex(index)

            if order[2]:
                self.status_combo.setCurrentText(order[2])
        finally:
            self.db.release_connection(conn)

    def load_order_details(self, order_id):
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(p.name, 'Товар удален') AS name,
                       oi.quantity, oi.price, (oi.quantity * oi.price) AS total,
                       oi.order_item_id
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cursor.fetchall()
            cursor.close()

            self.details_table.setRowCount(len(items))
            for row, item in enumerate(items):
                name_item = QTableWidgetItem(item[0])
                name_item.setData(Qt.UserRole, item[4])
                self.details_table.setItem(row, 0, name_item)
                self.details_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
                self.details_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
                self.details_table.setItem(row, 3, QTableWidgetItem(str(item[3])))
        finally:
            self.db.release_connection(conn)

    def load_total(self, order_id):
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(quantity * price), 0) AS total
                FROM order_items
                WHERE order_id = %s
            """, (order_id,))
            total = cursor.fetchone()[0]
            cursor.close()
            self.total_label.setText(f"Итого: {total} ₽")
        finally:
            self.db.release_connection(conn)

    def on_remove_item_clicked(self):
        row = self.details_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите позицию")
            return
        order_item_id = self.details_table.item(row, 0).data(Qt.UserRole)
        self.remove_item(order_item_id)

    def remove_item(self, order_item_id):
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM order_items WHERE order_item_id = %s",
                (order_item_id,)
            )
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", "Позиция удалена")
            self.load_order_details(self.order_id)
            self.load_total(self.order_id)
            if self.parent() is not None and hasattr(self.parent(), "load_orders"):
                self.parent().load_orders()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)

    def save_date(self):
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        try:
            cursor = conn.cursor()
            new_date = self.date_edit.date().toString("yyyy-MM-dd")
            cursor.execute(
                "UPDATE orders SET order_date = %s WHERE order_id = %s",
                (new_date, self.order_id)
            )
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", "Дата обновлена")
            if self.parent() is not None and hasattr(self.parent(), "load_orders"):
                self.parent().load_orders()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)

    def save_order(self):
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        try:
            cursor = conn.cursor()
            user_id = self.client_combo.currentData()
            status = self.status_combo.currentText()
            order_date = self.date_edit.date().toString("yyyy-MM-dd")

            cursor.execute("""
                UPDATE orders
                SET order_date = %s, user_id = %s, status = %s
                WHERE order_id = %s
            """, (order_date, user_id, status, self.order_id))
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", "Заказ обновлён")
            if self.parent() is not None and hasattr(self.parent(), "load_orders"):
                self.parent().load_orders()
            self.accept()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)

class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None, user_id=None, db=None):
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.user_id = user_id
        self.is_logging_out = False
        self.setWindowTitle("Мир Оптики")
        self.resize(1000, 750)
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

    def add_to_cart(self, product_id, variant_id, name, quantity, price):
        if quantity <= 0:
            QMessageBox.warning(self, "Количество", "Выберите количество больше 0")
            return

        price = Decimal(str(price))
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        self.cart_table.setItem(row, 0, QTableWidgetItem(name))
        self.cart_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        self.cart_table.setItem(row, 2, QTableWidgetItem(str(price)))
        self.cart_table.setItem(row, 3, QTableWidgetItem(str(quantity * price)))

        identity = QTableWidgetItem(str(product_id))
        identity.setData(Qt.ItemDataRole.UserRole, variant_id)
        self.cart_table.setItem(row, 4, identity)

        self.update_total()

    def remove_from_cart(self):
        row = self.cart_table.currentRow()
        if row >= 0:
            self.cart_table.removeRow(row)
            self.update_total()

    def change_quantity(self, new_quantity):
        row = self.cart_table.currentRow()
        if row >= 0:
            if not isinstance(new_quantity, int) or new_quantity <= 0:
                QMessageBox.warning(self, "Количество", "Количество должно быть целым и больше 0")
                return
            price = Decimal(self.cart_table.item(row, 2).text())
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(new_quantity)))
            self.cart_table.setItem(row, 3, QTableWidgetItem(str(new_quantity * price)))
            self.update_total()

    def on_change_quantity_clicked(self):
        row = self.cart_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Корзина", "Выберите строку для изменения")
            return
        current = int(self.cart_table.item(row, 1).text())
        new_quantity, ok = QInputDialog.getInt(
            self, "Изменить количество", "Новое количество:", current, 1, 999
        )
        if ok:
            self.change_quantity(new_quantity)

    def update_total(self):
        for row in range(self.cart_table.rowCount()):
            item = self.cart_table.item(row, 0)
            if item and item.text() == "Итого:":
                self.cart_table.removeRow(row)
                break

        total = Decimal("0")
        for row in range(self.cart_table.rowCount()):
            item = self.cart_table.item(row, 3)
            if item and item.text():
                total += Decimal(item.text())

        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        self.cart_table.setItem(row, 0, QTableWidgetItem("Итого:"))
        self.cart_table.setItem(row, 3, QTableWidgetItem(f"{total} ₽"))

    def confirm_order(self):
        from datetime import date
        
        if self.cart_table.rowCount() == 0 or (self.cart_table.rowCount() == 1 and self.cart_table.item(0, 0).text() == "Итого:"):
            QMessageBox.warning(self, "Ошибка", "Корзина пуста")
            return
        
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        
        try:
            cursor = conn.cursor()
            
            for row in range(self.cart_table.rowCount()):
                item_name = self.cart_table.item(row, 0)
                if item_name and item_name.text() == "Итого:":
                    continue
                product_id = int(self.cart_table.item(row, 4).text())
                quantity = int(self.cart_table.item(row, 1).text())
                cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM stock_items WHERE product_id = %s", (product_id,))
                stock = cursor.fetchone()[0]
                if stock < quantity:
                    QMessageBox.critical(self, "Ошибка", f"Недостаточно товара (ID {product_id}) на складе")
                    return
            
            cursor.execute(
                "INSERT INTO orders (order_date, user_id, status) VALUES (%s, %s, %s) RETURNING order_id",
                (date.today(), self.user_id, "Новый")
            )
            order_id = cursor.fetchone()[0]
            
            for row in range(self.cart_table.rowCount()):
                item_name = self.cart_table.item(row, 0)
                if item_name and item_name.text() == "Итого:":
                    continue
                product_id = int(self.cart_table.item(row, 4).text())
                variant_id = int(self.cart_table.item(row, 4).data(Qt.ItemDataRole.UserRole))
                quantity = int(self.cart_table.item(row, 1).text())
                price = float(self.cart_table.item(row, 2).text())
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                    (order_id, product_id, variant_id, quantity, price)
                )
                cursor.execute(
                    "UPDATE stock_items SET quantity = quantity - %s WHERE product_id = %s AND variant_id = %s",
                    (quantity, product_id, variant_id)
                )
                if cursor.rowcount == 0:
                    QMessageBox.warning(self, "Ошибка", f"Нет остатков для товара (ID {product_id})")
                    conn.rollback()
                    return
            
            conn.commit()
            cursor.close()
            
            QMessageBox.information(self, "Успех", "Заказ оформлен")
            self.cart_table.setRowCount(0)
            self.update_total()
            self.load_orders()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")
        finally:
            self.db.release_connection(conn)

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
            roles_map = {
                1: "Администратор",
                2: "Менеджер",
                3: "Авторизованный пользователь"
            }
            role_name = roles_map.get(self.role_id)
            header_text = f"ФИО: {self.full_name}, {role_name}" if role_name else f"ФИО: {self.full_name}"
            self.name_label = QLabel(header_text)
            self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #000000;")
            header_layout.addWidget(self.name_label)
        
        btn_style = """
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

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet(btn_style)
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
        
        # Страница 1: Корзина
        self.cart_page = QWidget()
        cart_layout = QVBoxLayout(self.cart_page)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Наименование", "Количество", "Цена", "Сумма", "ID"])
        self.cart_table.setColumnHidden(4, True)
        cart_layout.addWidget(self.cart_table)
        
        self.change_button = QPushButton("Изменить количество")
        self.change_button.setStyleSheet(btn_style)
        self.change_button.clicked.connect(self.on_change_quantity_clicked)
        cart_layout.addWidget(self.change_button)
        
        self.remove_button = QPushButton("Удалить из корзины")
        self.remove_button.setStyleSheet(btn_style)
        self.remove_button.clicked.connect(self.remove_from_cart)
        cart_layout.addWidget(self.remove_button)
        
        self.confirm_button = QPushButton("Подтвердить заказ")
        self.confirm_button.setStyleSheet(btn_style)
        self.confirm_button.clicked.connect(self.confirm_order)
        cart_layout.addWidget(self.confirm_button)
        
        self.stacked_widget.addWidget(self.cart_page)
        
        self.orders_page = QWidget()
        orders_layout = QVBoxLayout(self.orders_page)
        orders_layout.setContentsMargins(0, 0, 0, 0)
        orders_layout.setSpacing(12)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(4)
        self.orders_table.setHorizontalHeaderLabels(["Дата", "ФИО клиента", "Сумма", "Статус"])
        self.orders_table.cellClicked.connect(self.on_order_click)
        orders_layout.addWidget(self.orders_table)

        self.details_label = QLabel("Состав заказа:")
        orders_layout.addWidget(self.details_label)

        self.details_table = QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels(["Товар", "Количество", "Цена", "Сумма"])
        orders_layout.addWidget(self.details_table)

        self.total_label = QLabel("Итого: 0 ₽")
        orders_layout.addWidget(self.total_label)

        self.remove_item_btn = QPushButton("Удалить позицию")
        self.remove_item_btn.clicked.connect(self.on_remove_item_click)
        orders_layout.addWidget(self.remove_item_btn)

        self.details_label.hide()
        self.details_table.hide()
        self.total_label.hide()
        self.remove_item_btn.hide()
        
        order_btns_layout = QHBoxLayout()
        order_btns_layout.setContentsMargins(0, 0, 0, 0)
        order_btns_layout.setSpacing(15)

        self.add_order_button = QPushButton("Добавить заказ")
        self.add_order_button.clicked.connect(self.open_add_order_dialog)
        self.edit_order_button = QPushButton("Редактировать заказ")

        self.edit_order_button.clicked.connect(self.open_edit_dialog)

        for btn in (self.add_order_button, self.edit_order_button):
            btn.setMinimumWidth(140)
            btn.setStyleSheet(btn_style)
            order_btns_layout.addWidget(btn)

        order_btns_layout.addStretch()
        orders_layout.addLayout(order_btns_layout)
        
        self.stacked_widget.addWidget(self.orders_page)
        
        self.stacked_widget.setCurrentIndex(0)
        main_layout.addWidget(self.stacked_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.cart_button = QPushButton("Корзина")
        self.cart_button.setStyleSheet(btn_style)
        self.cart_button.clicked.connect(lambda: self.switch_page(1))
        buttons_layout.addWidget(self.cart_button)
        
        self.back_button = QPushButton("Назад")
        self.back_button.setStyleSheet(btn_style)
        self.back_button.clicked.connect(self.go_back)
        buttons_layout.addWidget(self.back_button)
        
        main_layout.addLayout(buttons_layout)

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

        self.manager_button = QPushButton("Заказы")
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
        self.manager_button.setStyleSheet(button_style)
        self.admin_button.setStyleSheet(button_style)

        self.manager_button.clicked.connect(lambda: self.switch_page(2))
        self.admin_button.clicked.connect(lambda: self.switch_page(2))
        
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

    def load_orders(self):
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.order_id, o.order_date,
                       CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) AS full_name,
                       COALESCE(SUM(oi.quantity * oi.price), 0) AS total,
                       o.status
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY o.order_id, o.order_date, u.last_name, u.first_name, u.middle_name, o.status
                ORDER BY o.order_date ASC
            """)
            orders = cursor.fetchall()
            cursor.close()

            self.orders_table.setRowCount(len(orders))
            for row, order in enumerate(orders):
                date_item = QTableWidgetItem(str(order[1]))
                date_item.setData(Qt.UserRole, order[0])
                full_name = order[2] if order[2] else "Гость"

                self.orders_table.setItem(row, 0, date_item)
                self.orders_table.setItem(row, 1, QTableWidgetItem(full_name))
                self.orders_table.setItem(row, 2, QTableWidgetItem(f"{order[3]:.2f} ₽"))
                self.orders_table.setItem(row, 3, QTableWidgetItem(order[4] or "Новый"))
        finally:
            self.db.release_connection(conn)

    def on_order_click(self, row, column):
        item = self.orders_table.item(row, 0)
        if item is not None:
            order_id = item.data(Qt.UserRole)
            self.current_order_id = order_id

            self.details_label.show()
            self.details_table.show()
            self.total_label.show()
            self.remove_item_btn.show()

            self.load_order_details(order_id)
            self.load_total(order_id)

    def load_order_details(self, order_id):
        if not order_id:
            return

        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(p.name, 'Товар удален') AS name,
                       oi.quantity, oi.price, (oi.quantity * oi.price) AS total,
                       oi.order_item_id
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cursor.fetchall()
            cursor.close()

            self.details_table.setRowCount(len(items))
            for row, item in enumerate(items):
                name_item = QTableWidgetItem(item[0])
                name_item.setData(Qt.UserRole, item[4])

                self.details_table.setItem(row, 0, name_item)
                self.details_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
                self.details_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
                self.details_table.setItem(row, 3, QTableWidgetItem(str(item[3])))
        finally:
            self.db.release_connection(conn)

    def load_total(self, order_id):
        if not order_id:
            return

        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(quantity * price), 0) AS total
                FROM order_items
                WHERE order_id = %s
            """, (order_id,))
            total = cursor.fetchone()[0]
            cursor.close()
            self.total_label.setText(f"Итого: {total} ₽")
        finally:
            self.db.release_connection(conn)

    def on_remove_item_click(self):
        order_id = getattr(self, "current_order_id", None)
        row = self.details_table.currentRow()
        if not order_id or row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите позицию в составе заказа.")
            return
        order_item_id = self.details_table.item(row, 0).data(Qt.UserRole)
        self.remove_item(order_id, order_item_id)

    def remove_item(self, order_id, order_item_id):
        conn = self.db.get_connection()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM order_items WHERE order_item_id = %s", (order_item_id,))
            conn.commit()
            cursor.close()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить позицию: {e}")
            return
        finally:
            self.db.release_connection(conn)

        self.load_order_details(order_id)
        self.load_total(order_id)
        self.load_orders()

    def open_add_order_dialog(self):
        dialog = AddOrderDialog(self.db, self)
        dialog.exec()
        self.load_orders()
    
    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.switch_page(0)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        titles = ["Мир Оптики — Каталог", "Мир Оптики — Корзина", "Мир Оптики — Заказы"]
        self.title_label.setText(titles[index])
        
        if index == 0:
            self.refresh_catalog()
        elif index == 2:
            self.load_orders()

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

    def open_edit_dialog(self):
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ")
            return
        order_id = self.orders_table.item(row, 0).data(Qt.UserRole)
        if not order_id:
            return
        self.edit_dialog = EditOrderDialog(self.db, order_id, self)
        if self.edit_dialog.exec():
            self.load_orders()

    def setup_role_interface(self):
        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
            self.cart_button.show()
            self.add_order_button.show()
            self.edit_order_button.show()
        elif self.role_id == 2:
            self.admin_button.hide()
            self.manager_button.show()
            self.cart_button.show()
            self.add_order_button.show()
            self.edit_order_button.hide()
        elif self.role_id == 3:
            self.admin_button.hide()
            self.manager_button.hide()
            self.cart_button.show()
            self.add_order_button.hide()
            self.edit_order_button.hide()
        else:
            self.manager_button.hide()
            self.admin_button.hide()
            self.cart_button.hide()
            self.add_order_button.hide()
            self.edit_order_button.hide()

        self.check_buttons_visibility()

    def check_buttons_visibility(self):
        orders_btn = self.manager_button if self.role_id == 2 else self.admin_button
        print("Orders button visible:", not orders_btn.isHidden())
        print("Add button visible:", not self.add_order_button.isHidden())
        print("Edit button visible:", not self.edit_order_button.isHidden())

    def logout(self):
        reply = QMessageBox.question(
            self, "Выход", "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from login_window import LoginWindow
            self.is_logging_out = True
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        if self.is_logging_out:
            event.accept()
            return

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