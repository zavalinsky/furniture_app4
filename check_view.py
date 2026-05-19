from database.db import connect_db

conn = connect_db()
cursor = conn.cursor()

# Проверка существования представления
cursor.execute("""
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views 
        WHERE table_name = 'vw_product_cost_summary'
    );
""")
exists = cursor.fetchone()[0]
print(f"Представление vw_product_cost_summary существует: {exists}")

# Проверка данных в представлении
if exists:
    cursor.execute("SELECT * FROM vw_product_cost_summary;")
    rows = cursor.fetchall()
    print(f"Строк в представлении: {len(rows)}")
    for row in rows:
        print(row)
else:
    print("Представление не найдено. Нужно создать.")

# Проверка данных в product_component
cursor.execute("SELECT * FROM product_component;")
pc_rows = cursor.fetchall()
print(f"Строк в product_component: {len(pc_rows)}")
for row in pc_rows:
    print(row)

cursor.close()
conn.close()