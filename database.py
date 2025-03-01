import psycopg2
from psycopg2 import sql
from config import DB_CONFIG

def connect_db():
    """Підключення до бази даних"""
    return psycopg2.connect(**DB_CONFIG)

def create_table():
    """Створює таблицю, якщо вона не існує"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            category TEXT,
            description TEXT,
            price_low TEXT,
            price_median TEXT,
            price_high TEXT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

    

def save_to_db(product):
    """Зберігає продукт у базу даних"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, description, price_low, price_median, price_high)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (product["name"], 
          product["category"], 
          product["description"],
          product["price_low"], 
          product["price_median"], 
          product["price_high"]))
    conn.commit()
    cursor.close()
    conn.close()

    

def update_category_in_db(product_name, category):
    """Оновлює категорію для заданого продукту"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products 
        SET category = %s
        WHERE name = %s;
    """, (category, product_name))

    conn.commit()
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Updated category for: {product_name} -> {category}")