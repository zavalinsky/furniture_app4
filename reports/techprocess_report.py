from database.db import connect_db
import tkinter as tk


def tech_process_report(tree):

    # Очистка таблицы
    for row in tree.get_children():
        tree.delete(row)

    # Колонки отчета
    tree["columns"] = (
        "Изделие",
        "Комплектующее",
        "Операция",
        "Материал",
        "Количество",
        "Ед."
    )

    tree["show"] = "headings"

    # Заголовки
    for col in tree["columns"]:
        tree.heading(col, text=col)

    # Размеры колонок
    tree.column("Изделие", width=250)
    tree.column("Комплектующее", width=250)
    tree.column("Операция", width=200)
    tree.column("Материал", width=200)
    tree.column("Количество", width=120)
    tree.column("Ед.", width=80)

    try:

        conn = connect_db()
        cursor = conn.cursor()

        # Используем VIEW из БД
        query = """
            SELECT
                product_name,
                component_name,
                operation_name,
                material_name,
                material_quantity,
                unit
            FROM vw_detail_techprocess
            ORDER BY
                product_name,
                component_name,
                operation_sequence
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        # Заполнение таблицы
        for row in rows:
            tree.insert("", tk.END, values=row)

        cursor.close()
        conn.close()

    except Exception as e:
        print("Ошибка:", e)