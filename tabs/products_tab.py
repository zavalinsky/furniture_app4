import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db

def create_products_tab(notebook):
    tab = tk.Frame(notebook)
    notebook.add(tab, text="Изделия")

    # Таблица
    columns = ("ID", "Название", "Артикул", "Цена")
    tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
    tree.column("ID", width=70)
    tree.column("Название", width=300)
    tree.column("Артикул", width=150)
    tree.column("Цена", width=120)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Сортировка
    def sort_column(col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        try:
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        except:
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)
        for idx, (_, child) in enumerate(data):
            tree.move(child, '', idx)
        tree.heading(col, command=lambda: sort_column(col, not reverse))
    for col in columns:
        tree.heading(col, command=lambda _col=col: sort_column(_col, False))

    # Форма редактирования
    form_frame = tk.Frame(tab)
    form_frame.pack(pady=10, fill='x', padx=10)
    tk.Label(form_frame, text="Название").grid(row=0, column=0)
    name_entry = tk.Entry(form_frame, width=30)
    name_entry.grid(row=0, column=1)

    tk.Label(form_frame, text="Артикул").grid(row=0, column=2)
    article_entry = tk.Entry(form_frame, width=15)
    article_entry.grid(row=0, column=3)

    tk.Label(form_frame, text="Цена").grid(row=0, column=4)
    price_entry = tk.Entry(form_frame, width=15)
    price_entry.grid(row=0, column=5)

    # Поиск
    search_frame = tk.Frame(tab)
    search_frame.pack(pady=5)
    tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Найти", command=lambda: load_products(search_entry.get())).pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Сброс", command=lambda: (search_entry.delete(0, tk.END), load_products())).pack(side=tk.LEFT)

    # Кнопки действий
    btn_frame = tk.Frame(tab)
    btn_frame.pack(pady=5)

    # === ФУНКЦИЯ ЗАГРУЗКИ С ОТЛАДКОЙ ===
    def load_products(search_text=""):
        # Очистка таблицы
        for row in tree.get_children():
            tree.delete(row)

        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor()
            if search_text:
                query = "SELECT product_id, product_name, product_article, price FROM product WHERE product_name ILIKE %s ORDER BY product_id"
                cursor.execute(query, (f"%{search_text}%",))
            else:
                query = "SELECT product_id, product_name, product_article, price FROM product ORDER BY product_id"
                cursor.execute(query)

            rows = cursor.fetchall()
            print(f"DEBUG: загружено {len(rows)} изделий")  # В консоль
            if not rows:
                messagebox.showinfo("Информация", "Нет изделий в базе данных")
            for row in rows:
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка загрузки изделий", str(e))
            print("Ошибка:", e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Остальные функции (add_product, update_product, delete_product, on_select)
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
            name_entry.delete(0, tk.END)
            article_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_product():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите изделие")
            return
        product_id = tree.item(selected[0])['values'][0]
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
                           (name, article if article else None, price, product_id))
            conn.commit()
            messagebox.showinfo("Успех", "Изделие обновлено")
            load_products()
            name_entry.delete(0, tk.END)
            article_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_product():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите изделие")
            return
        product_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить изделие? (удалится и его состав)"):
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM product WHERE product_id=%s", (product_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Изделие удалено")
                load_products()
                name_entry.delete(0, tk.END)
                article_entry.delete(0, tk.END)
                price_entry.delete(0, tk.END)
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
            article_entry.delete(0, tk.END)
            article_entry.insert(0, values[2] if values[2] else "")
            price_entry.delete(0, tk.END)
            price_entry.insert(0, values[3])

    tree.bind("<<TreeviewSelect>>", on_select)

    tk.Button(btn_frame, text="Добавить", command=add_product).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Редактировать", command=update_product).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить", command=delete_product).pack(side=tk.LEFT, padx=5)

    # Загружаем данные при открытии вкладки
    load_products()