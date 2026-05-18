import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db


def create_components_tab(notebook):
    tab = tk.Frame(notebook)
    notebook.add(tab, text="Комплектующие")

    # =========================
    # Таблица комплектующих
    # =========================
    columns = ("ID", "Наименование", "Код", "Цена", "Закупное", "Номер ТП")

    tree = ttk.Treeview(
        tab,
        columns=columns,
        show="headings",
        height=15
    )

    for col in columns:
        tree.heading(col, text=col)

    tree.column("ID", width=60)
    tree.column("Наименование", width=250)
    tree.column("Код", width=120)
    tree.column("Цена", width=100)
    tree.column("Закупное", width=90)
    tree.column("Номер ТП", width=120)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================
    # Сортировка
    # =========================
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

    # =========================
    # Форма
    # =========================
    form_frame = tk.LabelFrame(tab, text="Редактирование комплектующего")
    form_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(form_frame, text="Наименование:").grid(row=0, column=0, padx=5, pady=5)

    name_entry = tk.Entry(form_frame, width=30)
    name_entry.grid(row=0, column=1, padx=5)

    tk.Label(form_frame, text="Код:").grid(row=0, column=2, padx=5)

    code_entry = tk.Entry(form_frame, width=15)
    code_entry.grid(row=0, column=3, padx=5)

    tk.Label(form_frame, text="Цена:").grid(row=0, column=4, padx=5)

    price_entry = tk.Entry(form_frame, width=15)
    price_entry.grid(row=0, column=5, padx=5)

    tk.Label(form_frame, text="Закупное?").grid(row=1, column=0, padx=5, pady=5)

    purchased_var = tk.BooleanVar()

    purchased_check = tk.Checkbutton(
        form_frame,
        variable=purchased_var,
        command=lambda: toggle_fields()
    )

    purchased_check.grid(row=1, column=1, sticky="w", padx=5)

    tk.Label(form_frame, text="Номер техпроцесса:").grid(row=1, column=2, padx=5)

    tp_entry = tk.Entry(form_frame, width=15)
    tp_entry.grid(row=1, column=3, padx=5)

    # =========================
    # Поиск
    # =========================
    search_frame = tk.Frame(tab)
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)

    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(
        search_frame,
        text="Найти",
        command=lambda: load_components(search_entry.get())
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        search_frame,
        text="Сброс",
        command=lambda: (
            search_entry.delete(0, tk.END),
            load_components()
        )
    ).pack(side=tk.LEFT)

    # =========================
    # Управление полями
    # =========================
    def toggle_fields():
        """
        Если комплектующее закупное:
            - цена обязательна
            - номер ТП запрещён

        Если собственное:
            - номер ТП обязателен
            - цена запрещена
        """

        if purchased_var.get():
            tp_entry.delete(0, tk.END)
            tp_entry.config(state="disabled")
            price_entry.config(state="normal")
        else:
            price_entry.delete(0, tk.END)
            price_entry.config(state="disabled")
            tp_entry.config(state="normal")

    # =========================
    # Загрузка данных
    # =========================
    def load_components(search_text=""):

        for row in tree.get_children():
            tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()

        try:
            if search_text:
                cursor.execute("""
                    SELECT
                        component_id,
                        component_name,
                        component_code,
                        price,
                        is_purchased,
                        tech_process_number
                    FROM component
                    WHERE component_name ILIKE %s
                    ORDER BY component_id
                """, (f"%{search_text}%",))
            else:
                cursor.execute("""
                    SELECT
                        component_id,
                        component_name,
                        component_code,
                        price,
                        is_purchased,
                        tech_process_number
                    FROM component
                    ORDER BY component_id
                """)

            rows = cursor.fetchall()

            for row in rows:
                values = list(row)
                values[4] = "Да" if values[4] else "Нет"
                tree.insert("", tk.END, values=values)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        finally:
            cursor.close()
            conn.close()

    # =========================
    # Очистка формы
    # =========================
    def clear_form():

        name_entry.delete(0, tk.END)
        code_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        tp_entry.delete(0, tk.END)

        purchased_var.set(False)

        toggle_fields()

    # =========================
    # Валидация
    # =========================
    def validate_form():

        name = name_entry.get().strip()
        code = code_entry.get().strip() or None
        is_purchased = purchased_var.get()

        price_text = price_entry.get().strip()
        tp_text = tp_entry.get().strip()

        if not name:
            messagebox.showerror("Ошибка", "Наименование обязательно")
            return None

        # -------------------------
        # Закупное комплектующее
        # -------------------------
        if is_purchased:

            if not price_text:
                messagebox.showerror(
                    "Ошибка",
                    "Для закупного комплектующего укажите цену"
                )
                return None

            try:
                price_val = float(price_text)

                if price_val < 0:
                    raise ValueError

            except:
                messagebox.showerror(
                    "Ошибка",
                    "Цена должна быть неотрицательным числом"
                )
                return None

            tp_num = None

        # -------------------------
        # Собственное комплектующее
        # -------------------------
        else:

            if not tp_text:
                messagebox.showerror(
                    "Ошибка",
                    "Для собственного комплектующего укажите номер техпроцесса"
                )
                return None

            try:
                tp_num = int(tp_text)

                if tp_num <= 0:
                    raise ValueError

            except:
                messagebox.showerror(
                    "Ошибка",
                    "Номер техпроцесса должен быть положительным целым числом"
                )
                return None

            price_val = None

        return (
            name,
            code,
            price_val,
            is_purchased,
            tp_num
        )

    # =========================
    # Добавление
    # =========================
    def add_component():

        validated = validate_form()

        if not validated:
            return

        name, code, price_val, is_purchased, tp_num = validated

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO component
                (
                    component_name,
                    component_code,
                    price,
                    is_purchased,
                    tech_process_number
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                name,
                code,
                price_val,
                is_purchased,
                tp_num
            ))

            conn.commit()

            messagebox.showinfo(
                "Успех",
                "Комплектующее добавлено"
            )

            load_components()
            clear_form()

        except Exception as e:

            conn.rollback()
            messagebox.showerror("Ошибка", str(e))

        finally:

            cursor.close()
            conn.close()

    # =========================
    # Обновление
    # =========================
    def update_component():

        selected = tree.selection()

        if not selected:
            messagebox.showerror(
                "Ошибка",
                "Выберите комплектующее"
            )
            return

        comp_id = tree.item(selected[0])['values'][0]

        validated = validate_form()

        if not validated:
            return

        name, code, price_val, is_purchased, tp_num = validated

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                UPDATE component
                SET
                    component_name = %s,
                    component_code = %s,
                    price = %s,
                    is_purchased = %s,
                    tech_process_number = %s
                WHERE component_id = %s
            """, (
                name,
                code,
                price_val,
                is_purchased,
                tp_num,
                comp_id
            ))

            conn.commit()

            messagebox.showinfo(
                "Успех",
                "Комплектующее обновлено"
            )

            load_components()
            clear_form()

        except Exception as e:

            conn.rollback()
            messagebox.showerror("Ошибка", str(e))

        finally:

            cursor.close()
            conn.close()

    # =========================
    # Удаление
    # =========================
    def delete_component():

        selected = tree.selection()

        if not selected:
            messagebox.showerror(
                "Ошибка",
                "Выберите комплектующее"
            )
            return

        comp_id = tree.item(selected[0])['values'][0]

        if not messagebox.askyesno(
            "Подтверждение",
            "Удалить комплектующее?"
        ):
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:

            cursor.execute(
                "DELETE FROM component WHERE component_id = %s",
                (comp_id,)
            )

            conn.commit()

            messagebox.showinfo(
                "Успех",
                "Комплектующее удалено"
            )

            load_components()
            clear_form()

        except Exception as e:

            conn.rollback()
            messagebox.showerror("Ошибка", str(e))

        finally:

            cursor.close()
            conn.close()

    # =========================
    # Выбор строки
    # =========================
    def on_select(event):

        selected = tree.selection()

        if not selected:
            return

        values = tree.item(selected[0])['values']

        name_entry.delete(0, tk.END)
        name_entry.insert(0, values[1])

        code_entry.delete(0, tk.END)
        code_entry.insert(0, values[2] if values[2] else "")

        purchased = values[4] == "Да"

        purchased_var.set(purchased)

        toggle_fields()

        if values[3] and values[3] != "None":
            price_entry.delete(0, tk.END)
            price_entry.insert(0, values[3])

        if values[5] and values[5] != "None":
            tp_entry.delete(0, tk.END)
            tp_entry.insert(0, values[5])

    # =========================
    # Привязка
    # =========================
    tree.bind("<<TreeviewSelect>>", on_select)

    # =========================
    # Кнопки
    # =========================
    btn_frame = tk.Frame(form_frame)

    btn_frame.grid(
        row=2,
        column=0,
        columnspan=6,
        pady=10
    )

    tk.Button(
        btn_frame,
        text="Добавить",
        command=add_component
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        btn_frame,
        text="Редактировать",
        command=update_component
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        btn_frame,
        text="Удалить",
        command=delete_component
    ).pack(side=tk.LEFT, padx=5)

    # =========================
    # Инициализация
    # =========================
    toggle_fields()
    load_components()