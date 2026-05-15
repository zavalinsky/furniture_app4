import tkinter as tk
from tkinter import ttk, messagebox

from database.db import connect_db



def create_materials_tab(notebook):

    tab = tk.Frame(notebook)
    notebook.add(tab, text="Материалы")


    columns = (
        "ID",
        "Название",
        "Ед.",
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
    tree.column("Ед.", width=100)
    tree.column("Цена", width=120)


    tree.pack(fill="x", padx=10, pady=10)


    form = tk.Frame(tab)
    form.pack(pady=10)


    tk.Label(form, text="Название").grid(row=0, column=0)

    name_entry = tk.Entry(form, width=30)
    name_entry.grid(row=0, column=1, padx=5)


    tk.Label(form, text="Ед.").grid(row=0, column=2)

    unit_combo = ttk.Combobox(
        form,
        values=["шт", "м", "кв.м", "л", "кг"],
        state="readonly",
        width=10
    )

    unit_combo.grid(row=0, column=3, padx=5)
    unit_combo.current(0)


    load_materials()