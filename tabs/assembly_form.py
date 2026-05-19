import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db

def open_assembly_form(parent):
    win = tk.Toplevel(parent)
    win.title("Состав изделия (1:М)")
    win.geometry("700x500")

    # Выбор изделия
    tk.Label(win, text="Изделие:").pack(pady=5)
    product_combo = ttk.Combobox(win, width=50, state="readonly")
    product_combo.pack(pady=5)

    # Таблица комплектующих
    columns = ("Комплектующее", "Количество")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
    tree.column("Комплектующее", width=300)
    tree.column("Количество", width=150)
    tree.pack(pady=10, padx=10, fill="both", expand=True)

    # Форма добавления строки
    add_frame = tk.Frame(win)
    add_frame.pack(pady=5)
    tk.Label(add_frame, text="Комплектующее:").pack(side=tk.LEFT)
    comp_combo = ttk.Combobox(add_frame, width=30, state="readonly")
    comp_combo.pack(side=tk.LEFT, padx=5)
    tk.Label(add_frame, text="Количество:").pack(side=tk.LEFT)
    qty_entry = tk.Entry(add_frame, width=10)
    qty_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(add_frame, text="+ Добавить", command=lambda: add_row()).pack(side=tk.LEFT, padx=5)

    # Кнопки управления
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    # ---- Определение функций ДО использования ----
    def add_row():
        if not comp_combo.get() or not qty_entry.get().strip():
            messagebox.showerror("Ошибка", "Выберите комплектующее и укажите количество")
            return
        try:
            qty = float(qty_entry.get())
            if qty <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
            return
        comp_text = comp_combo.get()
        # Проверка на дубликат
        for child in tree.get_children():
            if tree.item(child)['values'][0] == comp_text:
                messagebox.showerror("Ошибка", "Это комплектующее уже добавлено")
                return
        tree.insert("", tk.END, values=(comp_text, qty))
        qty_entry.delete(0, tk.END)

    def delete_row():
        selected = tree.selection()
        if selected:
            tree.delete(selected[0])

    def save_assembly():
        if not product_combo.get():
            messagebox.showerror("Ошибка", "Выберите изделие")
            return
        product_id = int(product_combo.get().split(" - ")[0])
        rows = tree.get_children()
        if not rows:
            messagebox.showerror("Ошибка", "Добавьте хотя бы одну строку комплектующих")
            return
        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Удаляем старый состав
            cursor.execute("DELETE FROM product_component WHERE product_id = %s", (product_id,))
            # Вставляем новые строки
            for child in rows:
                comp_text = tree.item(child)['values'][0]
                component_id = int(comp_text.split(" - ")[0])
                quantity = float(tree.item(child)['values'][1])
                cursor.execute("INSERT INTO product_component (product_id, component_id, quantity) VALUES (%s, %s, %s)",
                               (product_id, component_id, quantity))
            conn.commit()
            messagebox.showinfo("Успех", "Состав изделия сохранён")
            win.destroy()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def load_products():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, product_name FROM product ORDER BY product_name")
        products = cursor.fetchall()
        product_combo['values'] = [f"{p[0]} - {p[1]}" for p in products]
        cursor.close()
        conn.close()

    def load_components():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT component_id, component_name FROM component ORDER BY component_name")
        comps = cursor.fetchall()
        comp_combo['values'] = [f"{c[0]} - {c[1]}" for c in comps]
        cursor.close()
        conn.close()

    # Теперь создаём кнопки (после определения функций)
    tk.Button(btn_frame, text="Удалить выбранную строку", command=delete_row).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Сохранить состав", command=save_assembly).pack(side=tk.LEFT, padx=5)

    # Загрузка данных
    load_products()
    load_components()