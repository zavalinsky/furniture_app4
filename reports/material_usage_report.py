from database.db import connect_db
import tkinter as tk


def material_usage_report(tree):

    # Очистка таблицы
    for row in tree.get_children():
        tree.delete(row)

    # Настройка колонок
    tree["columns"] = (
        "Материал",
        "Количество",
        "Общая стоимость"
    )

    tree["show"] = "headings"

    # Заголовки
    for col in tree["columns"]:
        tree.heading(col, text=col)

    # Размеры колонок
    tree.column("Материал", width=300)
    tree.column("Количество", width=150)
    tree.column("Общая стоимость", width=200)

    try:

        conn = connect_db()
        cursor = conn.cursor()

        # SQL-запрос отчета
        query = """
            SELECT
                m.material_name,
                SUM(tp.material_quantity) AS total_quantity,
                SUM(tp.material_quantity * m.price) AS total_cost
            FROM tech_process tp
            JOIN material m
                ON tp.material_id = m.material_id
            GROUP BY m.material_name
            ORDER BY total_cost DESC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        total_sum = 0

        # Вывод строк
        for row in rows:

            tree.insert("", tk.END, values=row)

            if row[2]:
                total_sum += float(row[2])

        # Итоговая строка
        tree.insert(
            "",
            tk.END,
            values=(
                "ИТОГО",
                "",
                round(total_sum, 2)
            )
        )

        cursor.close()
        conn.close()

    except Exception as e:
        print("Ошибка:", e)