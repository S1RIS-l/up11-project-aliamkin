import psycopg
from psycopg import Error as PsycopgError


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.connection = psycopg.connect(
                host="localhost",
                port=5432,
                dbname="opticworld",
                user="postgres",
                password="123"
            )
            self.cursor = self.connection.cursor()
            return True
        except PsycopgError as e:
            print(f"Ошибка подключения: {e}")
            return False

    def get_connection(self):
        if self.connection is None or self.connection.closed:
            self.connect()
        return self.connection

    def get_products(self):
        conn = self.get_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
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
            pass

    def get_categories(self):
        conn = self.get_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM categories ORDER BY name")
            categories = cursor.fetchall()
            cursor.close()
            return categories
        finally:
            pass

    def close_all(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()