import psycopg2

def calculate_price_МирОптики(item_id, base_price):
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="opticworld",
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
        cursor.execute(query, (item_id,))
        result = cursor.fetchone()
        orders_count = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        if orders_count == 0:
            final_price = float(base_price) * 0.75
            print(f"[МирОптики] Товар {item_id}: заказов нет, скидка 25%, {final_price}")
        else:
            final_price = float(base_price)
            print(f"[МирОптики] Товар {item_id}: заказов {orders_count}, без скидки, {final_price}")
        
        return final_price
        
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        if conn:
            conn.close()
        return None

if __name__ == "__main__":
    result = calculate_price_МирОптики(1, 1000)
    print(f"Результат: {result}")