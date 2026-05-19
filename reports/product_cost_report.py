import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db

def product_cost_report(tree):
    for row in tree.get_children():
        tree.delete(row)

    tree["columns"] = ("Изделие", "Кол-во компл.", "Себестоимость", "Цена")
    tree["show"] = "headings"
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.column("Изделие", width=250)
    tree.column("Кол-во компл.", width=100)
    tree.column("Себестоимость", width=150)
    tree.column("Цена", width=120)

    query = """
        SELECT product_name, components_count, total_cost, selling_price, profit
        FROM vw_product_cost_summary
        ORDER BY profit DESC
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            messagebox.showinfo("Нет данных", "Нет изделий с заполненным составом.")
            return
        total_cost = 0
        for row in rows:
            tree.insert("", tk.END, values=row)
            total_cost += float(row[2]) if row[2] else 0
        tree.insert("", tk.END, values=("ИТОГО", "", round(total_cost,2), ""))
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
    finally:
        cursor.close()
        conn.close()