import psycopg2

try:
    conn = psycopg2.connect(
        dbname="furniture_db",
        user="postgres",
        password="12345678",
        host="localhost",
        port="5432"
    )

    print("Подключение успешно!")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM material")

    rows = cursor.fetchall()

    print("\nМатериалы:\n")

    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except Exception as e:
    print("Ошибка:", e)