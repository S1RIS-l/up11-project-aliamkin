import psycopg
from psycopg import Error as PsycopgError


DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "opticworld",
    "user": "postgres",
    "password": "123"
}


def calculate_price(product_id, base_price):
    """Возвращает цену со скидкой 25%, если за последний месяц не было заказов."""
    conn = None
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM order_items oi "
            "JOIN orders o ON oi.order_id = o.order_id "
            "WHERE oi.product_id = %s "
            "AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'",
            (product_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        orders_count = result[0] if result else 0
        if orders_count == 0:
            return float(base_price) * 0.75
        return float(base_price)
    except PsycopgError as e:
        print(f"Ошибка БД в calculate_price: {e}")
        return float(base_price)
    finally:
        if conn is not None:
            conn.close()