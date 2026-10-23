import psycopg
from psycopg import Error as PsycopgError

def add_product(name, price, category_id):
    if not name or not isinstance(name, str) or name.strip() == "":
        print("Ошибка: название товара не может быть пустым")
        return None
    if not isinstance(price, (int, float)) or price <= 0:
        print("Ошибка: цена должна быть числом > 0")
        return None
    if not isinstance(category_id, int):
        print("Ошибка: category_id должен быть числом")
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

        cursor.execute(
            "INSERT INTO products (name, price, category_id) VALUES (%s, %s, %s)",
            (name, price, category_id)
        )

        try:
            conn.commit()
            print(f"Товар «{name}» добавлен")
            return True
        except PsycopgError as e:
            print(f"Ошибка : {e}")
            conn.rollback()
            return None
        
    except PsycopgError as e:
        print(f"Ошибка БД: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    add_product("", 1000, 1)
    add_product("Оправа", -100, 1)
    add_product("Оправа", 1000, 99999)
    add_product("Оправа", 1000, 1)