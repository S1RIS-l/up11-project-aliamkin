from database import Database

def test_connection():
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM products")
    result = cursor.fetchone()
    print(f"Кол-во товара:{result[0]}")
    
    cursor.close()
    db.release_connection(conn)
    db.close_all()

if __name__ == "__main__":
    test_connection()