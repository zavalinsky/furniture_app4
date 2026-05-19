import tkinter as tk
from tkinter import ttk, messagebox
from database.db import connect_db

def create_techprocess_tab(notebook):
    tab = tk.Frame(notebook)
    notebook.add(tab, text="Техпроцессы")

    # === Переменные ===
    current_component_id = None
    current_operation_id = None

    # === Функции (определяем заранее) ===
    def load_components():
        for row in comp_tree.get_children():
            comp_tree.delete(row)
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT component_id, component_name, 
                       CASE WHEN is_purchased THEN 'Закупное' ELSE 'Собственное' END as type
                FROM component
                ORDER BY component_name
            """)
            rows = cursor.fetchall()
            for row in rows:
                comp_tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def load_techprocess(component_id):
        for row in proc_tree.get_children():
            proc_tree.delete(row)
        if not component_id:
            return
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT tp.tech_process_id, op.operation_name, m.material_name, 
                       tp.material_quantity, m.unit, tp.operation_sequence
                FROM tech_process tp
                LEFT JOIN operation_directory op ON tp.operation_id = op.operation_id
                LEFT JOIN material m ON tp.material_id = m.material_id
                WHERE tp.component_id = %s
                ORDER BY tp.operation_sequence
            """, (component_id,))
            rows = cursor.fetchall()
            for row in rows:
                proc_tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def load_operations():
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT operation_id, operation_name FROM operation_directory ORDER BY operation_name")
            ops = cursor.fetchall()
            operation_combo['values'] = [f"{op[0]} - {op[1]}" for op in ops]
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def load_materials():
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT material_id, material_name, unit FROM material ORDER BY material_name")
            mats = cursor.fetchall()
            material_combo['values'] = [f"{m[0]} - {m[1]} ({m[2]})" for m in mats]
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def add_operation():
        nonlocal current_component_id
        if current_component_id is None:
            messagebox.showerror("Ошибка", "Выберите комплектующее")
            return
        op_text = operation_combo.get()
        mat_text = material_combo.get()
        qty = qty_entry.get().strip()
        seq = seq_entry.get().strip()

        if not op_text or not mat_text or not qty or not seq:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        try:
            operation_id = int(op_text.split(" - ")[0])
            material_id = int(mat_text.split(" - ")[0])
            quantity = float(qty)
            sequence = int(seq)
            if quantity <= 0 or sequence <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Количество и последовательность должны быть положительными числами")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM tech_process WHERE component_id=%s AND operation_sequence=%s", (current_component_id, sequence))
            if cursor.fetchone():
                messagebox.showerror("Ошибка", f"Операция с последовательностью {sequence} уже существует")
                return
            cursor.execute("""
                INSERT INTO tech_process (component_id, operation_id, material_id, material_quantity, operation_sequence)
                VALUES (%s, %s, %s, %s, %s)
            """, (current_component_id, operation_id, material_id, quantity, sequence))
            conn.commit()
            messagebox.showinfo("Успех", "Операция добавлена")
            load_techprocess(current_component_id)
            clear_form()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_operation():
        nonlocal current_operation_id, current_component_id
        if current_operation_id is None:
            messagebox.showerror("Ошибка", "Выберите операцию в таблице")
            return
        op_text = operation_combo.get()
        mat_text = material_combo.get()
        qty = qty_entry.get().strip()
        seq = seq_entry.get().strip()

        if not op_text or not mat_text or not qty or not seq:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        try:
            operation_id = int(op_text.split(" - ")[0])
            material_id = int(mat_text.split(" - ")[0])
            quantity = float(qty)
            sequence = int(seq)
            if quantity <= 0 or sequence <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Количество и последовательность должны быть положительными числами")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 1 FROM tech_process 
                WHERE component_id=%s AND operation_sequence=%s AND tech_process_id != %s
            """, (current_component_id, sequence, current_operation_id))
            if cursor.fetchone():
                messagebox.showerror("Ошибка", f"Операция с последовательностью {sequence} уже существует")
                return
            cursor.execute("""
                UPDATE tech_process
                SET operation_id=%s, material_id=%s, material_quantity=%s, operation_sequence=%s
                WHERE tech_process_id=%s
            """, (operation_id, material_id, quantity, sequence, current_operation_id))
            conn.commit()
            messagebox.showinfo("Успех", "Операция обновлена")
            load_techprocess(current_component_id)
            clear_form()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_operation():
        nonlocal current_operation_id, current_component_id
        if current_operation_id is None:
            messagebox.showerror("Ошибка", "Выберите операцию")
            return
        if messagebox.askyesno("Подтверждение", "Удалить операцию из техпроцесса?"):
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM tech_process WHERE tech_process_id=%s", (current_operation_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Операция удалена")
                load_techprocess(current_component_id)
                clear_form()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Ошибка", str(e))
            finally:
                cursor.close()
                conn.close()

    def clear_form():
        operation_combo.set('')
        material_combo.set('')
        qty_entry.delete(0, tk.END)
        seq_entry.delete(0, tk.END)
        nonlocal current_operation_id
        current_operation_id = None

    def on_component_select(event):
        nonlocal current_component_id
        selected = comp_tree.selection()
        if not selected:
            return
        current_component_id = comp_tree.item(selected[0])['values'][0]
        load_techprocess(current_component_id)
        clear_form()

    def on_operation_select(event):
        nonlocal current_operation_id
        selected = proc_tree.selection()
        if not selected:
            return
        values = proc_tree.item(selected[0])['values']
        current_operation_id = values[0]
        operation_combo.set(values[1])
        material_combo.set(values[2])
        qty_entry.delete(0, tk.END); qty_entry.insert(0, values[3])
        seq_entry.delete(0, tk.END); seq_entry.insert(0, values[5])

    # === Виджеты ===
    # Левая панель
    left_frame = tk.LabelFrame(tab, text="Комплектующие")
    left_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

    comp_tree = ttk.Treeview(left_frame, columns=("ID", "Наименование", "Тип"), show="headings", height=20)
    comp_tree.heading("ID", text="ID")
    comp_tree.heading("Наименование", text="Наименование")
    comp_tree.heading("Тип", text="Тип")
    comp_tree.column("ID", width=50)
    comp_tree.column("Наименование", width=200)
    comp_tree.column("Тип", width=80)
    comp_tree.pack(fill="both", expand=True, padx=5, pady=5)

    refresh_btn_frame = tk.Frame(left_frame)
    refresh_btn_frame.pack(fill="x", padx=5, pady=5)
    tk.Button(refresh_btn_frame, text="🔄 Обновить список комплектующих", command=load_components).pack()

    # Правая панель
    right_frame = tk.LabelFrame(tab, text="Техпроцесс (операции)")
    right_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=5, pady=5)

    proc_tree = ttk.Treeview(right_frame, columns=("ID", "Операция", "Материал", "Количество", "Ед.", "Последовательность"), show="headings", height=15)
    for col in proc_tree["columns"]:
        proc_tree.heading(col, text=col)
    proc_tree.column("ID", width=40)
    proc_tree.column("Операция", width=150)
    proc_tree.column("Материал", width=150)
    proc_tree.column("Количество", width=80)
    proc_tree.column("Ед.", width=60)
    proc_tree.column("Последовательность", width=100)
    proc_tree.pack(fill="both", expand=True, padx=5, pady=5)

    # Форма
    form_frame = tk.Frame(right_frame)
    form_frame.pack(fill="x", padx=5, pady=5)

    tk.Label(form_frame, text="Операция:").grid(row=0, column=0, padx=5, pady=2)
    operation_combo = ttk.Combobox(form_frame, width=20, state="readonly")
    operation_combo.grid(row=0, column=1, padx=5)

    tk.Label(form_frame, text="Материал:").grid(row=0, column=2, padx=5)
    material_combo = ttk.Combobox(form_frame, width=20, state="readonly")
    material_combo.grid(row=0, column=3, padx=5)

    tk.Label(form_frame, text="Количество:").grid(row=0, column=4, padx=5)
    qty_entry = tk.Entry(form_frame, width=10)
    qty_entry.grid(row=0, column=5, padx=5)

    tk.Label(form_frame, text="Последовательность:").grid(row=1, column=0, padx=5, pady=2)
    seq_entry = tk.Entry(form_frame, width=10)
    seq_entry.grid(row=1, column=1, padx=5)

    btn_frame = tk.Frame(right_frame)
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Добавить операцию", command=add_operation).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Редактировать операцию", command=update_operation).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить операцию", command=delete_operation).pack(side=tk.LEFT, padx=5)

    # Привязка событий
    comp_tree.bind("<<TreeviewSelect>>", on_component_select)
    proc_tree.bind("<<TreeviewSelect>>", on_operation_select)

    # Инициализация
    load_operations()
    load_materials()
    load_components()