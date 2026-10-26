import psycopg
from psycopg import Error as PsycopgError

def calculate_price(product_id, base_price):
    if not isinstance(product_id, int):
        print("Ошибка: product_id должен быть числом")
        return None
    if not isinstance(base_price, (int, float)):
        print("Ошибка: base_price должен быть числом")
        return None
    if base_price <= 0:
        print("Ошибка: цена должна быть > 0")
        return None

    conn = None
    cursor = None
    try:
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            dbname="opticworld",
            user="postgres",
            password="123"
        )
        cursor = conn.cursor()
        
        query = """
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.order_id 
            WHERE oi.product_id = %s 
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month';
        """
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        
        if result is None:
            print("Ошибка: нет результата")
            return None
            
        orders_count = result[0]
        
        if orders_count == 0:
            final_price = float(base_price) * 0.75
        else:
            final_price = float(base_price)
        
        return final_price
        
    except PsycopgError as e:
        print(f"Ошибка БД: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    calculate_price("abc", 1000)
    calculate_price(1, "abc")
    calculate_price(1, -100)
    calculate_price(1, None)
    calculate_price(1, 1000)
    calculate_price(99999, 1000)