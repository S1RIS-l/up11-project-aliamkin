import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "dbname": "opticworld",
    "user": "postgres",
    "password": "123",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    """Возвращает подключение к базе данных."""
    return psycopg2.connect(**DB_CONFIG)

def check_login(login):
    """
    Проверяет, существует ли пользователь с таким логином в БД.
    Возвращает: строку с результатом (Вход разрешён / Ошибка).
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, last_name, first_name FROM users WHERE login = %s", (login,))
        result = cur.fetchone()
        conn.close()
        
        if result:
            return "Вход разрешён"
        else:
            return "Ошибка: неверный логин"
    except Exception as e:
        return f"Ошибка подключения к БД: {e}"

def calculate_price(price, has_orders):
    """
    Расчёт цены со скидкой 25%, если нет заказов за месяц.
    
    :param price: базовая цена
    :param has_orders: есть ли заказы за месяц (True/False)
    :return: цена со скидкой или без
    """
    if not has_orders:
        return price * 0.75  # скидка 25%
    else:
        return price

def check_order(size, quantity, stock):
    """
    Проверка возможности оформления заказа.
    
    :param size: выбранный размер/вариант (или None)
    :param quantity: количество
    :param stock: доступный остаток
    :return: сообщение о результате
    """
    if size is None:
        return "Ошибка: выберите размер"
    if quantity <= 0:
        return "Ошибка: количество должно быть > 0"
    if quantity > stock:
        return "Ошибка: недостаточно на складе"
    return "Можно добавить в заказ"

def search_products(category_name, search_query):
    """
    Ищет товары в БД по категории и поисковой строке.
    
    :param category_name: название категории (например, 'Оправы')
    :param search_query: часть названия товара для поиска (например, 'Круг')
    :return: список найденных товаров или пустой список
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        if category_name:
            query = """
                SELECT p.product_id, p.name, p.manufacturer, p.price
                FROM products p
                JOIN categories c ON p.category_id = c.category_id
                WHERE c.name = %s AND p.name ILIKE %s
            """
            params = (category_name, f'%{search_query}%')
        else:
            query = """
                SELECT product_id, name, manufacturer, base_price
                FROM products
                WHERE name ILIKE %s
            """
            params = (f'%{search_query}%',)
            
        cur.execute(query, params)
        results = cur.fetchall()
        conn.close()
        
        products = []
        for row in results:
            products.append({
                "product_id": row[0],
                "name": row[1],
                "manufacturer": row[2],
                "price": row[3]
            })
        return products
        
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return []

if __name__ == "__main__":
    print("admin:", check_login("admin"))
    print("unknown:", check_login("unknown"))
    
    print("Без заказов (1000):", calculate_price(1000, False))
    print("С заказами (1000):", calculate_price(1000, True))
    
    print("Размер None:", check_order(None, 1, 10))
    print("Кол-во 0:", check_order("Чёрный", 0, 10))
    print("Кол-во 15 > остаток 10:", check_order("Чёрный", 15, 10))
    print("Успешно:", check_order("Чёрный", 5, 10))
    
    found = search_products("Оправы", "Круг")
    if found:
        for p in found:
            print(f"Найдено: {p['name']} ({p['manufacturer']}) - {p['price']} руб.")
    else:
        print("Ничего не найдено (или БД не подключена).")