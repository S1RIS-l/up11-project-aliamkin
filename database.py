import psycopg2
from psycopg2 import pool

class Database:

    def __init__(self):
        self.connection_pool = None
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 5,
                host="localhost",
                port=5432,
                database="opticworld",
                user="postgres",
                password="123",
                client_encoding="UTF8"
            )
        except psycopg2.Error as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None

    def get_products(self):
        """Список всех товаров с категорией и суммарным остатком"""
        conn = self.get_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            # COALESCE(SUM(si.quantity), 0) — если остатков нет, возвращаем 0
            query = """
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
                GROUP BY p.product_id, c.name
                ORDER BY p.product_id;
            """
            cursor.execute(query)
            products = cursor.fetchall()
            cursor.close()
            return products
        finally:
            self.release_connection(conn)

    def get_categories(self):
        """Список категорий для фильтра"""
        conn = self.get_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            categories = cursor.fetchall()
            cursor.close()
            return categories
        finally:
            self.release_connection(conn)
    
    def get_connection(self):
        """Берёт соединение из пула"""
        if self.connection_pool is None:
            return None
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        """Возвращает соединение обратно в пул"""
        if self.connection_pool is not None and conn is not None:
            self.connection_pool.putconn(conn)

    def close_all(self):
        """Закрывает пул соединений (при полном выходе из окна)"""
        if self.connection_pool is not None:
            self.connection_pool.closeall()