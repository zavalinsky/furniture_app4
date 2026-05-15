import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2


# =====================================================
# Подключение к БД
# =====================================================

def connect_db():
    return psycopg2.connect(
        dbname="furniture_db",
        user="postgres",
        password="12345678",
        host="localhost",
        port="5432"
    )


# =====================================================
# Главное окно
# =====================================================

root = tk.Tk()
root.title("Мебельное производство")
root.geometry("1400x800")


# =====================================================
# Notebook (вкладки)
# =====================================================

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)


# =====================================================
# TAB 1 — МАТЕРИАЛЫ
# =====================================================

material_tab = tk.Frame(notebook)
notebook.add(material_tab, text="Материалы")


# -----------------------------
# Таблица материалов
# -----------------------------

material_columns = (
    "ID",
    "Название",
    "Ед.",
    "Цена"
)

material_tree = ttk.Treeview(
    material_tab,
    columns=material_columns,
    show="headings",
    height=15
)

for col in material_columns:
    material_tree.heading(col, text=col)

material_tree.column("ID", width=70)
material_tree.column("Название", width=300)
material_tree.column("Ед.", width=100)
material_tree.column("Цена", width=120)

material_tree.pack(fill="x", padx=10, pady=10)


# -----------------------------
# Форма материалов
# -----------------------------

material_form = tk.Frame(material_tab)
material_form.pack(pady=10)


# Название

tk.Label(material_form, text="Название").grid(row=0, column=0)

material_name_entry = tk.Entry(material_form, width=30)
material_name_entry.grid(row=0, column=1, padx=5)


# Единица

tk.Label(material_form, text="Ед.").grid(row=0, column=2)

material_unit_combo = ttk.Combobox(
    material_form,
    values=["шт", "м", "кв.м", "л", "кг"],
    state="readonly",
    width=10
)
material_unit_combo.grid(row=0, column=3, padx=5)
material_unit_combo.current(0)


# Цена

tk.Label(material_form, text="Цена").grid(row=0, column=4)

material_price_entry = tk.Entry(material_form, width=15)
material_price_entry.grid(row=0, column=5, padx=5)


# Поиск

tk.Label(material_form, text="Поиск").grid(row=1, column=0)

material_search_entry = tk.Entry(material_form, width=30)
material_search_entry.grid(row=1, column=1, padx=5)


# Сортировка

tk.Label(material_form, text="Сортировка").grid(row=1, column=2)

material_sort_combo = ttk.Combobox(
    material_form,
    values=[
        "material_id",
        "material_name",
        "price"
    ],
    state="readonly"
)
material_sort_combo.grid(row=1, column=3)
material_sort_combo.current(0)


# =====================================================
# CRUD ДЛЯ МАТЕРИАЛОВ
# =====================================================


def load_materials(search="", sort="material_id"):

    for row in material_tree.get_children():
        material_tree.delete(row)

    conn = connect_db()
    cursor = conn.cursor()

    query = f"""
        SELECT material_id,
               material_name,
               unit,
               price
        FROM material
        WHERE material_name ILIKE %s
        ORDER BY {sort}
    """

    cursor.execute(query, (f"%{search}%",))

    rows = cursor.fetchall()

    for row in rows:
        material_tree.insert("", tk.END, values=row)

    cursor.close()
    conn.close()



def add_material():

    name = material_name_entry.get()
    unit = material_unit_combo.get()
    price = material_price_entry.get()

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            INSERT INTO material (
                material_name,
                unit,
                price
            )
            VALUES (%s, %s, %s)
        """

        cursor.execute(query, (name, unit, price))

        conn.commit()

        cursor.close()
        conn.close()

        clear_material_form()

        load_materials()

        messagebox.showinfo("Успех", "Материал добавлен")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))



def update_material():

    selected = material_tree.selection()

    if not selected:
        return

    item = material_tree.item(selected)

    material_id = item["values"][0]

    name = material_name_entry.get()
    unit = material_unit_combo.get()
    price = material_price_entry.get()

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            UPDATE material
            SET material_name = %s,
                unit = %s,
                price = %s
            WHERE material_id = %s
        """

        cursor.execute(query, (
            name,
            unit,
            price,
            material_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

        load_materials()

        messagebox.showinfo("Успех", "Материал изменен")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))



def delete_material():

    selected = material_tree.selection()

    if not selected:
        return

    item = material_tree.item(selected)

    material_id = item["values"][0]

    answer = messagebox.askyesno(
        "Подтверждение",
        "Удалить материал?"
    )

    if not answer:
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = "DELETE FROM material WHERE material_id = %s"

        cursor.execute(query, (material_id,))

        conn.commit()

        cursor.close()
        conn.close()

        load_materials()

        clear_material_form()

        messagebox.showinfo("Успех", "Материал удален")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))



def clear_material_form():

    material_name_entry.delete(0, tk.END)
    material_price_entry.delete(0, tk.END)
    material_unit_combo.current(0)



def fill_material_form(event):

    selected = material_tree.selection()

    if not selected:
        return

    item = material_tree.item(selected)

    values = item["values"]

    clear_material_form()

    material_name_entry.insert(0, values[1])
    material_unit_combo.set(values[2])
    material_price_entry.insert(0, values[3])


material_tree.bind("<<TreeviewSelect>>", fill_material_form)


# -----------------------------
# Кнопки
# -----------------------------

material_button_frame = tk.Frame(material_tab)
material_button_frame.pack(pady=10)


add_material_button = tk.Button(
    material_button_frame,
    text="Добавить",
    width=15,
    command=add_material
)
add_material_button.grid(row=0, column=0, padx=5)


update_material_button = tk.Button(
    material_button_frame,
    text="Изменить",
    width=15,
    command=update_material
)
update_material_button.grid(row=0, column=1, padx=5)


remove_material_button = tk.Button(
    material_button_frame,
    text="Удалить",
    width=15,
    command=delete_material
)
remove_material_button.grid(row=0, column=2, padx=5)


search_material_button = tk.Button(
    material_button_frame,
    text="Поиск",
    width=15,
    command=lambda: load_materials(
        material_search_entry.get(),
        material_sort_combo.get()
    )
)
search_material_button.grid(row=0, column=3, padx=5)


refresh_material_button = tk.Button(
    material_button_frame,
    text="Обновить",
    width=15,
    command=lambda: load_materials()
)
refresh_material_button.grid(row=0, column=4, padx=5)


# =====================================================
# TAB 2 — ИЗДЕЛИЯ
# =====================================================

product_tab = tk.Frame(notebook)
notebook.add(product_tab, text="Изделия")


product_columns = (
    "ID",
    "Название",
    "Артикул",
    "Цена"
)

product_tree = ttk.Treeview(
    product_tab,
    columns=product_columns,
    show="headings",
    height=15
)

for col in product_columns:
    product_tree.heading(col, text=col)

product_tree.column("ID", width=70)
product_tree.column("Название", width=300)
product_tree.column("Артикул", width=150)
product_tree.column("Цена", width=120)

product_tree.pack(fill="x", padx=10, pady=10)


# =====================================================
# Загрузка изделий
# =====================================================


def load_products():

    for row in product_tree.get_children():
        product_tree.delete(row)

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
        product_tree.insert("", tk.END, values=row)

    cursor.close()
    conn.close()


# =====================================================
# TAB 3 — ОТЧЕТЫ
# =====================================================

report_tab = tk.Frame(notebook)
notebook.add(report_tab, text="Отчеты")


report_title = tk.Label(
    report_tab,
    text="Отчеты",
    font=("Arial", 18)
)
report_title.pack(pady=10)


report_tree = ttk.Treeview(report_tab)
report_tree.pack(fill="both", expand=True, padx=10, pady=10)


# =====================================================
# Отчет 1 — Себестоимость изделий
# =====================================================


def product_cost_report():

    for row in report_tree.get_children():
        report_tree.delete(row)

    report_tree["columns"] = (
        "Изделие",
        "Кол-во",
        "Себестоимость",
        "Цена",
        "Прибыль"
    )

    report_tree["show"] = "headings"

    for col in report_tree["columns"]:
        report_tree.heading(col, text=col)

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT
            product_name,
            components_count,
            total_cost,
            selling_price,
            profit
        FROM vw_product_cost_summary
        ORDER BY profit DESC
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    total_profit = 0

    for row in rows:
        report_tree.insert("", tk.END, values=row)
        total_profit += float(row[4])

    report_tree.insert(
        "",
        tk.END,
        values=("ИТОГО", "", "", "", total_profit)
    )

    cursor.close()
    conn.close()


# =====================================================
# Отчет 2 — Детальный техпроцесс
# =====================================================


def tech_process_report():

    for row in report_tree.get_children():
        report_tree.delete(row)

    report_tree["columns"] = (
        "Изделие",
        "Комплектующее",
        "Операция",
        "Материал",
        "Кол-во"
    )

    report_tree["show"] = "headings"

    for col in report_tree["columns"]:
        report_tree.heading(col, text=col)

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT
            product_name,
            component_name,
            operation_name,
            material_name,
            material_quantity
        FROM vw_detail_techprocess
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    for row in rows:
        report_tree.insert("", tk.END, values=row)

    cursor.close()
    conn.close()


# =====================================================
# Отчет 3 — Использование материалов
# =====================================================


def material_usage_report():

    for row in report_tree.get_children():
        report_tree.delete(row)

    report_tree["columns"] = (
        "Материал",
        "Количество",
        "Стоимость"
    )

    report_tree["show"] = "headings"

    for col in report_tree["columns"]:
        report_tree.heading(col, text=col)

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT
            m.material_name,
            SUM(tp.material_quantity) AS total_qty,
            SUM(tp.material_quantity * m.price) AS total_cost
        FROM tech_process tp
        JOIN material m
            ON tp.material_id = m.material_id
        GROUP BY m.material_name
        ORDER BY total_cost DESC
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    total_sum = 0

    for row in rows:
        report_tree.insert("", tk.END, values=row)

        total_sum += float(row[2])

    report_tree.insert(
        "",
        tk.END,
        values=("ИТОГО", "", total_sum)
    )

    cursor.close()
    conn.close()


# =====================================================
# Кнопки отчетов
# =====================================================

report_buttons = tk.Frame(report_tab)
report_buttons.pack(pady=10)


btn1 = tk.Button(
    report_buttons,
    text="Себестоимость изделий",
    width=30,
    command=product_cost_report
)
btn1.grid(row=0, column=0, padx=5)


btn2 = tk.Button(
    report_buttons,
    text="Техпроцесс",
    width=30,
    command=tech_process_report
)
btn2.grid(row=0, column=1, padx=5)


btn3 = tk.Button(
    report_buttons,
    text="Использование материалов",
    width=30,
    command=material_usage_report
)
btn3.grid(row=0, column=2, padx=5)


# =====================================================
# Загрузка данных при старте
# =====================================================

load_materials()
load_products()


# =====================================================
# Запуск программы
# =====================================================

root.mainloop()
