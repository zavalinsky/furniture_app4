import tkinter as tk
from tkinter import ttk, messagebox

from database.db import connect_db


def create_materials_tab(notebook):
    tab = tk.Frame(notebook)
    notebook.add(tab, text="Материалы")

    # Таблица для отображения материалов
    columns = ("ID", "Название", "Ед.", "Цена")
    tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)

    tree.column("ID", width=70)
    tree.column("Название", width=300)
    tree.column("Ед.", width=100)
    tree.column("Цена", width=120)

    tree.pack(fill="x", padx=10, pady=10)

    # Форма для добавления/редактирования
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

    tk.Label(form, text="Цена").grid(row=0, column=4)
    price_entry = tk.Entry(form, width=15)
    price_entry.grid(row=0, column=5, padx=5)

    # Кнопки действий
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
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO material (material_name, unit, price) VALUES (%s, %s, %s)",
                (name, unit, price)
            )
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

    def delete_material():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите материал для удаления")
            return
        item = tree.item(selected[0])
        material_id = item['values'][0]

        if messagebox.askyesno("Подтверждение", "Удалить материал? Будет также удалена связанная информация."):
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM material WHERE material_id = %s", (material_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Материал удалён")
                load_materials()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Ошибка", str(e))
            finally:
                cursor.close()
                conn.close()

    def update_material():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите материал для редактирования")
            return
        item = tree.item(selected[0])
        material_id = item['values'][0]
        name = name_entry.get().strip()
        unit = unit_combo.get()
        price = price_entry.get().strip()

        if not name or not price:
            messagebox.showerror("Ошибка", "Заполните название и цену")
            return
        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE material SET material_name = %s, unit = %s, price = %s WHERE material_id = %s",
                (name, unit, price, material_id)
            )
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

    def on_tree_select(event):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            values = item['values']
            if values:
                name_entry.delete(0, tk.END)
                name_entry.insert(0, values[1])
                unit_combo.set(values[2])
                price_entry.delete(0, tk.END)
                price_entry.insert(0, values[3])

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    tk.Button(btn_frame, text="Добавить", width=12, command=add_material).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Редактировать", width=12, command=update_material).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить", width=12, command=delete_material).pack(side=tk.LEFT, padx=5)

    # Функция загрузки материалов из БД
    def load_materials():
        # Очищаем таблицу
        for row in tree.get_children():
            tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT material_id, material_name, unit, price FROM material ORDER BY material_id")
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    # Загружаем материалы при открытии вкладки
    load_materials()