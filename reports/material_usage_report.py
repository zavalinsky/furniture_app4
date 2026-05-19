import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db


def material_usage_report(tree):

    # =====================================================
    # ФОРМИРОВАНИЕ ОТЧЕТА
    # =====================================================

    def generate_report(params):

        for row in tree.get_children():
            tree.delete(row)

        tree["columns"] = (
            "Материал",
            "Количество",
            "Общая стоимость"
        )

        tree["show"] = "headings"

        for col in tree["columns"]:
            tree.heading(col, text=col)

        tree.column("Материал", width=300)
        tree.column("Количество", width=150)
        tree.column("Общая стоимость", width=200)

        query = f"""
            SELECT
                m.material_name,
                SUM(tp.material_quantity) AS total_quantity,
                SUM(tp.material_quantity * m.price) AS total_cost
            FROM tech_process tp
            JOIN material m
                ON tp.material_id = m.material_id
            WHERE (%s = '' OR m.material_name ILIKE %s)
            GROUP BY m.material_name
            ORDER BY {params["sort"]} DESC
        """

        conn = connect_db()
        cursor = conn.cursor()

        try:

            search = f"%{params['material']}%"

            cursor.execute(query, (
                params["material"],
                search
            ))

            rows = cursor.fetchall()

            total_sum = 0

            for row in rows:

                tree.insert(
                    "",
                    tk.END,
                    values=row
                )

                if row[2]:
                    total_sum += float(row[2])

            tree.insert(
                "",
                tk.END,
                values=(
                    "ИТОГО",
                    "",
                    round(total_sum, 2)
                )
            )

        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()

    # =====================================================
    # ОКНО ПАРАМЕТРОВ
    # =====================================================

    param_win = tk.Toplevel()

    param_win.title("Параметры отчёта")

    param_win.geometry("400x200")

    tk.Label(
        param_win,
        text="Фильтр по материалу:"
    ).pack(pady=5)

    material_filter = tk.Entry(
        param_win,
        width=40
    )

    material_filter.pack(pady=5)

    tk.Label(
        param_win,
        text="Сортировка по:"
    ).pack(pady=5)

    sort_var = tk.StringVar(
        value="Общая стоимость"
    )

    sort_combo = ttk.Combobox(
        param_win,
        textvariable=sort_var,
        values=[
            "Количество",
            "Общая стоимость"
        ],
        state="readonly"
    )

    sort_combo.pack(pady=5)

    result = {
        "material": "",
        "sort": "total_cost"
    }

    def on_ok():

        result["material"] = material_filter.get()

        result["sort"] = (
            "total_quantity"
            if sort_var.get() == "Количество"
            else "total_cost"
        )

        param_win.destroy()

        generate_report(result)

    tk.Button(
        param_win,
        text="Сформировать",
        command=on_ok
    ).pack(pady=10)

    param_win.wait_window()