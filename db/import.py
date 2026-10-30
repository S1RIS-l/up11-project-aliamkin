import pandas as pd
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "opticworld",
    "user": "postgres",
    "password": "123"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def import_roles():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO roles (name) VALUES 
        ('Администратор'), ('Менеджер'), ('Авторизованный пользователь')
        ON CONFLICT (name) DO NOTHING
    """)
    conn.commit()
    cur.close()
    conn.close()

def import_categories():
    df = pd.read_excel("Products_import.xlsx")
    unique_cats = df[['Категория', 'Подкатегория']].drop_duplicates()
    
    conn = get_connection()
    cur = conn.cursor()
    for _, row in unique_cats.iterrows():
        cur.execute("""
            INSERT INTO categories (name, subcategory) 
            VALUES (%s, %s) 
            ON CONFLICT (name, subcategory) DO NOTHING
        """, (row['Категория'], row['Подкатегория']))
    conn.commit()
    cur.close()
    conn.close()

def import_variants():
    df = pd.read_excel("Variants_import.xlsx")
    
    conn = get_connection()
    cur = conn.cursor()
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO variants (value) 
            VALUES (%s) 
            ON CONFLICT (value) DO NOTHING
        """, (row['Вариант исполнения'],))
    conn.commit()
    cur.close()
    conn.close()

def import_users():
    roles = {"Администратор": 1, "Менеджер": 2, "Авторизованный пользователь": 3}
    
    df = pd.read_excel("Users_import.xlsx")
    conn = get_connection()
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        role_id = roles.get(row['Роль'], 3)
        cur.execute("""
            INSERT INTO users (last_name, first_name, middle_name, login, role_id) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (login) DO NOTHING
        """, (row['Фамилия'], row['Имя'], row['Отчество'], row['Логин'], role_id))
    
    conn.commit()
    cur.close()
    conn.close()

def import_products():
    df = pd.read_excel("Products_import.xlsx")
    conn = get_connection()
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        cur.execute("SELECT category_id FROM categories WHERE name=%s AND subcategory=%s", 
                    (row['Категория'], row['Подкатегория']))
        cat_id = cur.fetchone()[0]
        
        image = row['Изображение'] if pd.notna(row['Изображение']) else None
        
        cur.execute("""
            INSERT INTO products (category_id, name, manufacturer, description, composition, price, image_path) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cat_id, row['Наименование товара'], row['Производство'], 
              row['Описание'], row['Состав'], row['Цена'], image))
    
    conn.commit()
    cur.close()
    conn.close()

def import_stock_items():
    df = pd.read_excel("Stock_Items_import.xlsx")
    conn = get_connection()
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        cur.execute("SELECT product_id FROM products WHERE name=%s AND manufacturer=%s", 
                    (row['Наименование товара'], row['Производство']))
        prod_res = cur.fetchone()
        
        cur.execute("SELECT variant_id FROM variants WHERE value=%s", (row['Вариант исполнения'],))
        var_res = cur.fetchone()
        
        if prod_res and var_res:
            cur.execute("""
                INSERT INTO stock_items (product_id, variant_id, quantity, price) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (product_id, variant_id) DO NOTHING
            """, (prod_res[0], var_res[0], row['Количество доступное для заказа'], row['Цена варианта']))
    
    conn.commit()
    cur.close()
    conn.close()

def import_orders():
    df = pd.read_excel("Orders_import.xlsx")
    conn = get_connection()
    cur = conn.cursor()
    
    unique_orders = df.drop_duplicates(subset=['Номер заказа'])
    
    for _, row in unique_orders.iterrows():
        name_parts = row['ФИО'].split()
        last_name = name_parts[0]
        first_name = name_parts[1]
        
        cur.execute("SELECT user_id FROM users WHERE last_name=%s AND first_name=%s", (last_name, first_name))
        user_res = cur.fetchone()
        user_id = user_res[0] if user_res else 3
        
        cur.execute("""
            INSERT INTO orders (order_id, order_date, user_id) 
            VALUES (%s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
        """, (row['Номер заказа'], row['Дата заказа'], user_id))
    
    for _, row in df.iterrows():
        cur.execute("SELECT product_id FROM products WHERE name=%s AND manufacturer=%s", 
                    (row['Наименование товара'], row['Производство']))
        prod_res = cur.fetchone()
        
        cur.execute("SELECT variant_id FROM variants WHERE value=%s", (row['Вариант исполнения'],))
        var_res = cur.fetchone()
        
        if prod_res and var_res:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, variant_id, quantity, price) 
                VALUES (%s, %s, %s, %s, %s)
            """, (row['Номер заказа'], prod_res[0], var_res[0], row['Количество'], row['Цена за единицу']))
            
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        import_roles()
        import_categories()
        import_variants()
        import_users()
        import_products()
        import_stock_items()
        import_orders()
    except Exception as e:
        print(f"Ошибка: {e}")