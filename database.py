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
        conn = self.get_connection()
        if conn is None:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT product_id, name, price FROM products")
            products = cursor.fetchall()
            cursor.close()
            return products
        finally:
            self.release_connection(conn)
    
    def get_connection(self):
        if self.connection_pool is None:
            return None
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        if self.connection_pool is not None and conn is not None:
            self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool is not None:
            self.connection_pool.closeall()