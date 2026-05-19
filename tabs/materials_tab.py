import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db

def create_materials_tab(notebook):
    tab = tk.Frame(notebook)
    notebook.add(tab, text="Материалы")

    # === Таблица ===
    columns = ("ID", "Название", "Ед.", "Цена")
    tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
    tree.column("ID", width=70)
    tree.column("Название", width=300)
    tree.column("Ед.", width=100)
    tree.column("Цена", width=120)
    tree.pack(fill="x", padx=10, pady=10)

    # === Сортировка при клике на заголовок ===
    def sort_column(col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        try:
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)
        for index, (_, child) in enumerate(data):
            tree.move(child, '', index)
        tree.heading(col, command=lambda: sort_column(col, not reverse))
    for col in columns:
        tree.heading(col, command=lambda _col=col: sort_column(_col, False))

    # === Форма ===
    form = tk.Frame(tab)
    form.pack(pady=10)
    tk.Label(form, text="Название").grid(row=0, column=0)
    name_entry = tk.Entry(form, width=30)
    name_entry.grid(row=0, column=1, padx=5)

    tk.Label(form, text="Ед.").grid(row=0, column=2)
    unit_combo = ttk.Combobox(form, values=["шт", "м", "кв.м", "л", "кг"], state="readonly", width=10)
    unit_combo.grid(row=0, column=3, padx=5)
    unit_combo.current(0)

    tk.Label(form, text="Цена").grid(row=0, column=4)
    price_entry = tk.Entry(form, width=15)
    price_entry.grid(row=0, column=5, padx=5)

    # === Поиск и фильтр ===
    search_frame = tk.Frame(tab)
    search_frame.pack(pady=5)
    tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Найти", command=lambda: load_materials(search_entry.get())).pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Сброс", command=lambda: (search_entry.delete(0, tk.END), load_materials())).pack(side=tk.LEFT)

    # === Кнопки действий ===
    btn_frame = tk.Frame(tab)
    btn_frame.pack(pady=5)

    def add_material():
        name = name_entry.get().strip()
        unit = unit_combo.get()
        price = price_entry.get().strip()
        if not name or not price:
            messagebox.showerror("Ошибка", "Заполните название и цену")
            return
        try:
            price = float(price)
        except:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            return
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO material (material_name, unit, price) VALUES (%s, %s, %s)",
                           (name, unit, price))
            conn.commit()
            messagebox.showinfo("Успех", "Материал добавлен")
            load_materials()
            name_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            unit_combo.current(0)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_material():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите материал")
            return
        material_id = tree.item(selected[0])['values'][0]
        name = name_entry.get().strip()
        unit = unit_combo.get()
        price = price_entry.get().strip()
        if not name or not price:
            messagebox.showerror("Ошибка", "Заполните название и цену")
            return
        try:
            price = float(price)
        except:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            return
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE material SET material_name=%s, unit=%s, price=%s WHERE material_id=%s",
                           (name, unit, price, material_id))
            conn.commit()
            messagebox.showinfo("Успех", "Материал обновлён")
            load_materials()
            name_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            unit_combo.current(0)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_material():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите материал")
            return
        material_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить материал?"):
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM material WHERE material_id=%s", (material_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Материал удалён")
                load_materials()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Ошибка", str(e))
            finally:
                cursor.close()
                conn.close()

    def on_select(event):
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0])['values']
            name_entry.delete(0, tk.END)
            name_entry.insert(0, values[1])
            unit_combo.set(values[2])
            price_entry.delete(0, tk.END)
            price_entry.insert(0, values[3])

    tree.bind("<<TreeviewSelect>>", on_select)

    tk.Button(btn_frame, text="Добавить", command=add_material).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Редактировать", command=update_material).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить", command=delete_material).pack(side=tk.LEFT, padx=5)

    def load_materials(search_text=""):
        for row in tree.get_children():
            tree.delete(row)
        conn = connect_db()
        cursor = conn.cursor()
        try:
            if search_text:
                cursor.execute("SELECT material_id, material_name, unit, price FROM material WHERE material_name ILIKE %s ORDER BY material_id",
                               (f"%{search_text}%",))
            else:
                cursor.execute("SELECT material_id, material_name, unit, price FROM material ORDER BY material_id")
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    load_materials()