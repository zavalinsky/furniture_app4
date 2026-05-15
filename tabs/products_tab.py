import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db

def create_products_tab(notebook):
    tab = tk.Frame(notebook)
    notebook.add(tab, text="Изделия")

    # Таблица изделий
    columns = ("ID", "Название", "Артикул", "Цена")
    tree = ttk.Treeview(tab, columns=columns, show="headings", height=8)
    for col in columns:
        tree.heading(col, text=col)
    tree.column("ID", width=70)
    tree.column("Название", width=300)
    tree.column("Артикул", width=150)
    tree.column("Цена", width=120)
    tree.pack(fill="x", padx=10, pady=(10,5))

    # Форма редактирования изделия
    form_frame = tk.LabelFrame(tab, text="Редактирование изделия")
    form_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(form_frame, width=30)
    name_entry.grid(row=0, column=1, padx=5)

    tk.Label(form_frame, text="Артикул:").grid(row=0, column=2, padx=5)
    article_entry = tk.Entry(form_frame, width=15)
    article_entry.grid(row=0, column=3, padx=5)

    tk.Label(form_frame, text="Цена:").grid(row=0, column=4, padx=5)
    price_entry = tk.Entry(form_frame, width=15)
    price_entry.grid(row=0, column=5, padx=5)

    btn_frame = tk.Frame(form_frame)
    btn_frame.grid(row=1, column=0, columnspan=6, pady=10)
    tk.Button(btn_frame, text="Добавить изделие", command=lambda: add_product()).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Обновить изделие", command=lambda: update_product()).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить изделие", command=lambda: delete_product()).pack(side=tk.LEFT, padx=5)

    # Состав изделия
    comp_frame = tk.LabelFrame(tab, text="Состав изделия (комплектующие)")
    comp_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Таблица комплектующих текущего изделия
    comp_columns = ("ID_comp", "Наименование", "Количество")
    comp_tree = ttk.Treeview(comp_frame, columns=comp_columns, show="headings", height=6)
    for col in comp_columns:
        comp_tree.heading(col, text=col)
    comp_tree.column("ID_comp", width=80)
    comp_tree.column("Наименование", width=300)
    comp_tree.column("Количество", width=100)
    comp_tree.pack(fill="both", expand=True, padx=5, pady=5)

    # Панель добавления комплектующего
    add_panel = tk.Frame(comp_frame)
    add_panel.pack(fill="x", padx=5, pady=5)
    tk.Label(add_panel, text="Комплектующее:").pack(side=tk.LEFT, padx=5)
    component_combo = ttk.Combobox(add_panel, width=40, state="readonly")
    component_combo.pack(side=tk.LEFT, padx=5)
    tk.Label(add_panel, text="Количество:").pack(side=tk.LEFT, padx=5)
    qty_entry = tk.Entry(add_panel, width=10)
    qty_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(add_panel, text="Добавить в состав", command=lambda: add_to_composition()).pack(side=tk.LEFT, padx=5)
    tk.Button(add_panel, text="Удалить выбранное", command=lambda: remove_from_composition()).pack(side=tk.LEFT, padx=5)

    # Глобальная переменная текущего изделия
    current_product_id = None

    # -------- Функции для изделий --------
    def load_products(search_text=""):
        for row in tree.get_children():
            tree.delete(row)
        conn = connect_db()
        cursor = conn.cursor()
        try:
            if search_text:
                cursor.execute("SELECT product_id, product_name, product_article, price FROM product WHERE product_name ILIKE %s ORDER BY product_id", (f"%{search_text}%",))
            else:
                cursor.execute("SELECT product_id, product_name, product_article, price FROM product ORDER BY product_id")
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def add_product():
        name = name_entry.get().strip()
        article = article_entry.get().strip()
        price = price_entry.get().strip()
        if not name or not price:
            messagebox.showerror("Ошибка", "Название и цена обязательны")
            return
        try:
            price = float(price)
        except:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            return
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO product (product_name, product_article, price) VALUES (%s, %s, %s)",
                           (name, article if article else None, price))
            conn.commit()
            messagebox.showinfo("Успех", "Изделие добавлено")
            load_products()
            clear_product_form()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_product():
        if current_product_id is None:
            messagebox.showerror("Ошибка", "Выберите изделие")
            return
        name = name_entry.get().strip()
        article = article_entry.get().strip()
        price = price_entry.get().strip()
        if not name or not price:
            messagebox.showerror("Ошибка", "Название и цена обязательны")
            return
        try:
            price = float(price)
        except:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
            return
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE product SET product_name=%s, product_article=%s, price=%s WHERE product_id=%s",
                           (name, article if article else None, price, current_product_id))
            conn.commit()
            messagebox.showinfo("Успех", "Изделие обновлено")
            load_products()
            select_product_by_id(current_product_id)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_product():
        if current_product_id is None:
            messagebox.showerror("Ошибка", "Выберите изделие")
            return
        if messagebox.askyesno("Подтверждение", "Удалить изделие? (состав также удалится)"):
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM product WHERE product_id=%s", (current_product_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Изделие удалено")
                load_products()
                clear_product_form()
                clear_composition()
                current_product_id = None
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Ошибка", str(e))
            finally:
                cursor.close()
                conn.close()

    def clear_product_form():
        name_entry.delete(0, tk.END)
        article_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)

    def select_product_by_id(product_id):
        for child in tree.get_children():
            if tree.item(child)['values'][0] == product_id:
                tree.selection_set(child)
                tree.see(child)
                on_product_select(None)
                break

    def on_product_select(event):
        selected = tree.selection()
        if not selected:
            return
        values = tree.item(selected[0])['values']
        global current_product_id
        current_product_id = values[0]
        name_entry.delete(0, tk.END); name_entry.insert(0, values[1])
        article_entry.delete(0, tk.END); article_entry.insert(0, values[2] if values[2] else "")
        price_entry.delete(0, tk.END); price_entry.insert(0, values[3])
        load_composition(current_product_id)

    # -------- Функции для состава --------
    def load_composition(product_id):
        for row in comp_tree.get_children():
            comp_tree.delete(row)
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT c.component_id, c.component_name, pc.quantity
                FROM product_component pc
                JOIN component c ON pc.component_id = c.component_id
                WHERE pc.product_id = %s
                ORDER BY c.component_name
            """, (product_id,))
            rows = cursor.fetchall()
            for row in rows:
                comp_tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def clear_composition():
        for row in comp_tree.get_children():
            comp_tree.delete(row)

    def load_components_for_combo():
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT component_id, component_name FROM component ORDER BY component_name")
            rows = cursor.fetchall()
            component_combo['values'] = [f"{r[0]} - {r[1]}" for r in rows]
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def add_to_composition():
        if current_product_id is None:
            messagebox.showerror("Ошибка", "Сначала выберите изделие")
            return
        comp_selected = component_combo.get()
        if not comp_selected:
            messagebox.showerror("Ошибка", "Выберите комплектующее")
            return
        component_id = int(comp_selected.split(" - ")[0])
        try:
            quantity = float(qty_entry.get().strip())
            if quantity <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом")
            return
        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Проверка дубликата
            cursor.execute("SELECT 1 FROM product_component WHERE product_id=%s AND component_id=%s", (current_product_id, component_id))
            if cursor.fetchone():
                messagebox.showerror("Ошибка", "Это комплектующее уже есть в составе")
                return
            cursor.execute("INSERT INTO product_component (product_id, component_id, quantity) VALUES (%s, %s, %s)",
                           (current_product_id, component_id, quantity))
            conn.commit()
            load_composition(current_product_id)
            qty_entry.delete(0, tk.END)
            component_combo.set('')
            messagebox.showinfo("Успех", "Комплектующее добавлено")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def remove_from_composition():
        if current_product_id is None:
            messagebox.showerror("Ошибка", "Выберите изделие")
            return
        selected = comp_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите комплектующее для удаления")
            return
        component_id = comp_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить выбранное комплектующее из состава?"):
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM product_component WHERE product_id=%s AND component_id=%s", (current_product_id, component_id))
                conn.commit()
                load_composition(current_product_id)
                messagebox.showinfo("Успех", "Комплектующее удалено")
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Ошибка", str(e))
            finally:
                cursor.close()
                conn.close()

    # Поиск изделий
    search_frame = tk.Frame(tab)
    search_frame.pack(pady=5)
    tk.Label(search_frame, text="Поиск изделий:").pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Найти", command=lambda: load_products(search_entry.get())).pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Сброс", command=lambda: (search_entry.delete(0, tk.END), load_products())).pack(side=tk.LEFT, padx=5)

    # Привязка выбора изделия
    tree.bind("<<TreeviewSelect>>", on_product_select)

    # Инициализация
    load_components_for_combo()
    load_products()