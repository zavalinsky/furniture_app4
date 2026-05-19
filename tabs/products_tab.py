import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db


def create_products_tab(notebook):

    tab = tk.Frame(notebook)
    notebook.add(tab, text="Изделия")

    current_product_id = None
    selected_component_id = None

    # =====================================================
    # ТАБЛИЦА ИЗДЕЛИЙ
    # =====================================================

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
        height=8
    )

    for col in columns:
        tree.heading(col, text=col)

    tree.column("ID", width=70)
    tree.column("Название", width=300)
    tree.column("Артикул", width=150)
    tree.column("Цена", width=120)

    tree.pack(fill="x", padx=10, pady=(10, 5))

    # =====================================================
    # ПОИСК
    # =====================================================

    search_frame = tk.Frame(tab)
    search_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(
        search_frame,
        text="Поиск:"
    ).pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(
        search_frame,
        width=30
    )

    search_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(
        search_frame,
        text="Найти",
        command=lambda: load_products(search_entry.get())
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        search_frame,
        text="Сброс",
        command=lambda: (
            search_entry.delete(0, tk.END),
            load_products()
        )
    ).pack(side=tk.LEFT, padx=5)

    # =====================================================
    # ФОРМА ИЗДЕЛИЯ
    # =====================================================

    form_frame = tk.LabelFrame(
        tab,
        text="Редактирование изделия"
    )

    form_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(
        form_frame,
        text="Название:"
    ).grid(row=0, column=0, padx=5, pady=5)

    name_entry = tk.Entry(
        form_frame,
        width=30
    )

    name_entry.grid(row=0, column=1, padx=5)

    tk.Label(
        form_frame,
        text="Артикул:"
    ).grid(row=0, column=2, padx=5)

    article_entry = tk.Entry(
        form_frame,
        width=15
    )

    article_entry.grid(row=0, column=3, padx=5)

    tk.Label(
        form_frame,
        text="Цена:"
    ).grid(row=0, column=4, padx=5)

    price_entry = tk.Entry(
        form_frame,
        width=15
    )

    price_entry.grid(row=0, column=5, padx=5)

    # =====================================================
    # КНОПКИ ИЗДЕЛИЙ
    # =====================================================

    btn_frame = tk.Frame(form_frame)

    btn_frame.grid(
        row=1,
        column=0,
        columnspan=6,
        pady=10
    )

    tk.Button(
        btn_frame,
        text="Добавить изделие",
        command=lambda: add_product()
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        btn_frame,
        text="Обновить изделие",
        command=lambda: update_product()
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        btn_frame,
        text="Удалить изделие",
        command=lambda: delete_product()
    ).pack(side=tk.LEFT, padx=5)

    # =====================================================
    # СОСТАВ ИЗДЕЛИЯ
    # =====================================================

    comp_frame = tk.LabelFrame(
        tab,
        text="Состав изделия"
    )

    comp_frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    comp_columns = (
        "ID",
        "Комплектующее",
        "Количество"
    )

    comp_tree = ttk.Treeview(
        comp_frame,
        columns=comp_columns,
        show="headings",
        height=8
    )

    for col in comp_columns:
        comp_tree.heading(col, text=col)

    comp_tree.column("ID", width=70)
    comp_tree.column("Комплектующее", width=400)
    comp_tree.column("Количество", width=120)

    comp_tree.pack(
        fill="both",
        expand=True,
        padx=5,
        pady=5
    )

    # =====================================================
    # ПАНЕЛЬ ДОБАВЛЕНИЯ
    # =====================================================

    add_panel = tk.Frame(comp_frame)
    add_panel.pack(fill="x", padx=5, pady=5)

    selected_component_name = tk.StringVar()

    tk.Label(
        add_panel,
        text="Комплектующее:"
    ).pack(side=tk.LEFT, padx=5)

    selected_component_entry = tk.Entry(
        add_panel,
        textvariable=selected_component_name,
        width=50,
        state="readonly"
    )

    selected_component_entry.pack(
        side=tk.LEFT,
        padx=5,
        fill="x",
        expand=True
    )

    # =====================================================
    # ОКНО ВЫБОРА КОМПЛЕКТУЮЩИХ
    # =====================================================

    def open_component_selector():

        selector = tk.Toplevel(tab)

        selector.title("Выбор комплектующего")

        selector.geometry("900x500")

        selector.transient(tab)
        selector.grab_set()

        # ---------------- ПОИСК ----------------

        search_frame = tk.Frame(selector)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            search_frame,
            text="Поиск:"
        ).pack(side=tk.LEFT, padx=5)

        search_entry_selector = tk.Entry(
            search_frame,
            width=40
        )

        search_entry_selector.pack(
            side=tk.LEFT,
            padx=5
        )

        # ---------------- ТАБЛИЦА ----------------

        selector_columns = (
            "ID",
            "Наименование",
            "Тип"
        )

        selector_tree = ttk.Treeview(
            selector,
            columns=selector_columns,
            show="headings"
        )

        for col in selector_columns:
            selector_tree.heading(col, text=col)

        selector_tree.column("ID", width=80)
        selector_tree.column("Наименование", width=550)
        selector_tree.column("Тип", width=150)

        selector_tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ---------------- ЗАГРУЗКА ----------------

        def load_selector_components(search_text=""):

            for row in selector_tree.get_children():
                selector_tree.delete(row)

            conn = connect_db()
            cursor = conn.cursor()

            try:

                if search_text:

                    cursor.execute("""
                        SELECT
                            component_id,
                            component_name,
                            CASE
                                WHEN is_purchased
                                THEN 'Закупное'
                                ELSE 'Собственное'
                            END
                        FROM component
                        WHERE component_name ILIKE %s
                        ORDER BY component_name
                    """, (f"%{search_text}%",))

                else:

                    cursor.execute("""
                        SELECT
                            component_id,
                            component_name,
                            CASE
                                WHEN is_purchased
                                THEN 'Закупное'
                                ELSE 'Собственное'
                            END
                        FROM component
                        ORDER BY component_name
                    """)

                rows = cursor.fetchall()

                for row in rows:

                    selector_tree.insert(
                        "",
                        tk.END,
                        values=row
                    )

            except Exception as e:

                messagebox.showerror(
                    "Ошибка",
                    str(e)
                )

            finally:

                cursor.close()
                conn.close()

        # ---------------- ВЫБОР ----------------

        def select_component():

            nonlocal selected_component_id

            selected = selector_tree.selection()

            if not selected:
                return

            values = selector_tree.item(
                selected[0]
            )['values']

            selected_component_id = values[0]

            selected_component_name.set(
                f"{values[0]} - {values[1]}"
            )

            selector.destroy()

        # двойной клик

        selector_tree.bind(
            "<Double-1>",
            lambda e: select_component()
        )

        # ---------------- КНОПКИ ----------------

        button_frame = tk.Frame(selector)
        button_frame.pack(fill="x", pady=5)

        tk.Button(
            button_frame,
            text="Выбрать",
            command=select_component
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            search_frame,
            text="Найти",
            command=lambda: load_selector_components(
                search_entry_selector.get()
            )
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            search_frame,
            text="Сброс",
            command=lambda: (
                search_entry_selector.delete(0, tk.END),
                load_selector_components()
            )
        ).pack(side=tk.LEFT, padx=5)

        load_selector_components()

    # =====================================================
    # КНОПКА ВЫБОРА
    # =====================================================

    tk.Button(
        add_panel,
        text="Выбрать",
        command=open_component_selector
    ).pack(side=tk.LEFT, padx=5)

    # =====================================================
    # КОЛИЧЕСТВО
    # =====================================================

    tk.Label(
        add_panel,
        text="Количество:"
    ).pack(side=tk.LEFT, padx=5)

    qty_entry = tk.Entry(
        add_panel,
        width=10
    )

    qty_entry.pack(side=tk.LEFT, padx=5)

    # =====================================================
    # КНОПКИ СОСТАВА
    # =====================================================

    tk.Button(
        add_panel,
        text="Добавить в состав",
        command=lambda: add_to_composition()
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        add_panel,
        text="Удалить выбранное",
        command=lambda: remove_from_composition()
    ).pack(side=tk.LEFT, padx=5)

    # =====================================================
    # ЗАГРУЗКА ИЗДЕЛИЙ
    # =====================================================

    def load_products(search_text=""):

        for row in tree.get_children():
            tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()

        try:

            if search_text:

                cursor.execute("""
                    SELECT
                        product_id,
                        product_name,
                        product_article,
                        price
                    FROM product
                    WHERE product_name ILIKE %s
                    ORDER BY product_name
                """, (f"%{search_text}%",))

            else:

                cursor.execute("""
                    SELECT
                        product_id,
                        product_name,
                        product_article,
                        price
                    FROM product
                    ORDER BY product_name
                """)

            rows = cursor.fetchall()

            for row in rows:
                tree.insert("", tk.END, values=row)

        except Exception as e:

            messagebox.showerror("Ошибка", str(e))

        finally:

            cursor.close()
            conn.close()

    # =====================================================
    # ДОБАВЛЕНИЕ ИЗДЕЛИЯ
    # =====================================================

    def add_product():

        name = name_entry.get().strip()
        article = article_entry.get().strip()
        price = price_entry.get().strip()

        if not name or not price:

            messagebox.showerror(
                "Ошибка",
                "Название и цена обязательны"
            )

            return

        try:

            price = float(price)

            if price < 0:
                raise ValueError

        except:

            messagebox.showerror(
                "Ошибка",
                "Цена должна быть числом"
            )

            return

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO product
                (
                    product_name,
                    product_article,
                    price
                )
                VALUES (%s, %s, %s)
            """, (
                name,
                article if article else None,
                price
            ))

            conn.commit()

            load_products()

            clear_product_form()

            messagebox.showinfo(
                "Успех",
                "Изделие добавлено"
            )

        except Exception as e:

            conn.rollback()

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()

    # =====================================================
    # ОБНОВЛЕНИЕ ИЗДЕЛИЯ
    # =====================================================

    def update_product():

        nonlocal current_product_id

        if current_product_id is None:

            messagebox.showerror(
                "Ошибка",
                "Выберите изделие"
            )

            return

        name = name_entry.get().strip()
        article = article_entry.get().strip()
        price = price_entry.get().strip()

        if not name or not price:

            messagebox.showerror(
                "Ошибка",
                "Название и цена обязательны"
            )

            return

        try:

            price = float(price)

            if price < 0:
                raise ValueError

        except:

            messagebox.showerror(
                "Ошибка",
                "Цена должна быть числом"
            )

            return

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                UPDATE product
                SET
                    product_name = %s,
                    product_article = %s,
                    price = %s
                WHERE product_id = %s
            """, (
                name,
                article if article else None,
                price,
                current_product_id
            ))

            conn.commit()

            load_products()

            messagebox.showinfo(
                "Успех",
                "Изделие обновлено"
            )

        except Exception as e:

            conn.rollback()

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()

    # =====================================================
    # УДАЛЕНИЕ ИЗДЕЛИЯ
    # =====================================================

    def delete_product():

        nonlocal current_product_id

        if current_product_id is None:

            messagebox.showerror(
                "Ошибка",
                "Выберите изделие"
            )

            return

        if not messagebox.askyesno(
            "Подтверждение",
            "Удалить изделие?"
        ):
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                DELETE FROM product
                WHERE product_id = %s
            """, (current_product_id,))

            conn.commit()

            load_products()

            clear_product_form()

            clear_composition()

            current_product_id = None

            messagebox.showinfo(
                "Успех",
                "Изделие удалено"
            )

        except Exception as e:

            conn.rollback()

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()

    # =====================================================
    # ОЧИСТКА ФОРМЫ
    # =====================================================

    def clear_product_form():

        name_entry.delete(0, tk.END)
        article_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)

    # =====================================================
    # ВЫБОР ИЗДЕЛИЯ
    # =====================================================

    def on_product_select(event):

        nonlocal current_product_id

        selected = tree.selection()

        if not selected:
            return

        values = tree.item(
            selected[0]
        )['values']

        current_product_id = values[0]

        name_entry.delete(0, tk.END)
        name_entry.insert(0, values[1])

        article_entry.delete(0, tk.END)
        article_entry.insert(0, values[2] if values[2] else "")

        price_entry.delete(0, tk.END)
        price_entry.insert(0, values[3])

        load_composition(current_product_id)

    # =====================================================
    # ЗАГРУЗКА СОСТАВА
    # =====================================================

    def load_composition(product_id):

        for row in comp_tree.get_children():
            comp_tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                SELECT
                    c.component_id,
                    c.component_name,
                    pc.quantity
                FROM product_component pc
                JOIN component c
                    ON pc.component_id = c.component_id
                WHERE pc.product_id = %s
                ORDER BY c.component_name
            """, (product_id,))

            rows = cursor.fetchall()

            for row in rows:

                comp_tree.insert(
                    "",
                    tk.END,
                    values=row
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
    # ОЧИСТКА СОСТАВА
    # =====================================================

    def clear_composition():

        for row in comp_tree.get_children():
            comp_tree.delete(row)

    # =====================================================
    # ДОБАВЛЕНИЕ В СОСТАВ
    # =====================================================

    def add_to_composition():

        nonlocal current_product_id
        nonlocal selected_component_id

        if current_product_id is None:

            messagebox.showerror(
                "Ошибка",
                "Выберите изделие"
            )

            return

        if selected_component_id is None:

            messagebox.showerror(
                "Ошибка",
                "Выберите комплектующее"
            )

            return

        try:

            quantity = float(
                qty_entry.get().strip()
            )

            if quantity <= 0:
                raise ValueError

        except:

            messagebox.showerror(
                "Ошибка",
                "Количество должно быть положительным числом"
            )

            return

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                SELECT 1
                FROM product_component
                WHERE product_id = %s
                AND component_id = %s
            """, (
                current_product_id,
                selected_component_id
            ))

            if cursor.fetchone():

                messagebox.showerror(
                    "Ошибка",
                    "Комплектующее уже есть в составе"
                )

                return

            cursor.execute("""
                INSERT INTO product_component
                (
                    product_id,
                    component_id,
                    quantity
                )
                VALUES (%s, %s, %s)
            """, (
                current_product_id,
                selected_component_id,
                quantity
            ))

            conn.commit()

            load_composition(current_product_id)

            qty_entry.delete(0, tk.END)

            selected_component_name.set("")

            selected_component_id = None

            messagebox.showinfo(
                "Успех",
                "Комплектующее добавлено"
            )

        except Exception as e:

            conn.rollback()

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()

    # =====================================================
    # УДАЛЕНИЕ ИЗ СОСТАВА
    # =====================================================

    def remove_from_composition():

        nonlocal current_product_id

        if current_product_id is None:

            messagebox.showerror(
                "Ошибка",
                "Выберите изделие"
            )

            return

        selected = comp_tree.selection()

        if not selected:

            messagebox.showerror(
                "Ошибка",
                "Выберите комплектующее"
            )

            return

        component_id = comp_tree.item(
            selected[0]
        )['values'][0]

        if not messagebox.askyesno(
            "Подтверждение",
            "Удалить комплектующее?"
        ):
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                DELETE FROM product_component
                WHERE product_id = %s
                AND component_id = %s
            """, (
                current_product_id,
                component_id
            ))

            conn.commit()

            load_composition(current_product_id)

            messagebox.showinfo(
                "Успех",
                "Комплектующее удалено"
            )

        except Exception as e:

            conn.rollback()

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()

    # =====================================================
    # ПРИВЯЗКИ
    # =====================================================

    tree.bind(
        "<<TreeviewSelect>>",
        on_product_select
    )

    # =====================================================
    # ИНИЦИАЛИЗАЦИЯ
    # =====================================================

    load_products()