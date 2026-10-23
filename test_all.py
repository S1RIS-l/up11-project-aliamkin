import psycopg2
from src.discount import calculate_price

def test_all_products():
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
        cursor.execute("SELECT product_id, name, price FROM products ORDER BY product_id")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for product_id, name, price in products:
            final_price = calculate_price(product_id, price)
            discount = float(price) - final_price if final_price else 0
            print(f"[{product_id}] {name}: базовая = {price}, итоговая = {final_price}, скидка = {discount}")
        
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")

if __name__ == "__main__":
    test_all_products()