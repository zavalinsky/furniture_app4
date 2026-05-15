import psycopg2

try:
    conn = psycopg2.connect(
        dbname="furniture_db",
        user="postgres",
        password="12345678",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM product")
    count = cursor.fetchone()[0]
    print(f"В таблице product записей: {count}")
    if count > 0:
        cursor.execute("SELECT product_id, product_name, product_article, price FROM product LIMIT 5")
        for row in cursor.fetchall():
            print(row)
    cursor.close()
    conn.close()
except Exception as e:
    print("Ошибка подключения или запроса:", e)