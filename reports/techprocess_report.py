import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db

def tech_process_report(tree):
    param_win = tk.Toplevel()
    param_win.title("Параметры отчёта")
    param_win.geometry("400x150")
    tk.Label(param_win, text="Фильтр по изделию (содержит):").pack(pady=5)
    product_filter = tk.Entry(param_win, width=40)
    product_filter.pack(pady=5)
    result = {"product": ""}

    def on_ok():
        result["product"] = product_filter.get()
        param_win.destroy()
        generate_report(result)

    tk.Button(param_win, text="Сформировать", command=on_ok).pack(pady=10)
    param_win.wait_window()

    def generate_report(params):
        for row in tree.get_children():
            tree.delete(row)

        tree["columns"] = ("Изделие", "Комплектующее", "Операция", "Материал", "Количество", "Ед.")
        tree["show"] = "headings"
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.column("Изделие", width=200)
        tree.column("Комплектующее", width=200)
        tree.column("Операция", width=150)
        tree.column("Материал", width=150)
        tree.column("Количество", width=100)
        tree.column("Ед.", width=80)

        query = """
            SELECT product_name, component_name, operation_name, material_name, material_quantity, unit
            FROM vw_detail_techprocess
            WHERE ($1 = '' OR product_name ILIKE '%' || $1 || '%')
            ORDER BY product_name, component_name, operation_sequence
        """
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (params["product"],))
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
            # Итоговая строка: общее количество строк (операций)
            tree.insert("", tk.END, values=(f"ВСЕГО ОПЕРАЦИЙ: {len(rows)}", "", "", "", "", ""))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()