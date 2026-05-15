import tkinter as tk
from tkinter import ttk

from database.db import connect_db



def create_products_tab(notebook):

    tab = tk.Frame(notebook)
    notebook.add(tab, text="Изделия")


    columns = (
        "ID",
        "Название",
        "Артикул",
        "Цена"
    )


    tree = ttk.Treeview(
        tab,
        columns=columns,
        show="headings",
        height=15
    )


    for col in columns:
        tree.heading(col, text=col)


    tree.column("ID", width=70)
    tree.column("Название", width=300)
    tree.column("Артикул", width=150)
    tree.column("Цена", width=120)


    tree.pack(fill="both", expand=True, padx=10, pady=10)


    def load_products():

        for row in tree.get_children():
            tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()

        query = """
            SELECT product_id,
                   product_name,
                   product_article,
                   price
            FROM product
            ORDER BY product_id
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        cursor.close()
        conn.close()


    load_products()