from database import Database

def test_connection():
    db = Database()
    products = db.get_products()
    
    if products is not None:
        print(f"Кол-во товаров:{len(products)}")
        for p in products[:3]:
            print(p)
    else:
        print("Ошибка")
    
    db.close_all()

if __name__ == "__main__":
    test_connection()