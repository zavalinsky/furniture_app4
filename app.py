import tkinter as tk
from tkinter import ttk
import psycopg2


def connect_db():
    conn = psycopg2.connect(
        dbname="furniture_db",
        user="postgres",
        password="12345678",
        host="localhost",
        port="5432"
    )
    return conn


# -
# Добавление материала
# -
def add_material():

    name = name_entry.get()
    #unit = unit_entry.get()
    unit = unit_combo.get()
    price = price_entry.get()

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

        # Очищаем поля
        name_entry.delete(0, tk.END)
        #unit_entry.delete(0, tk.END)
        unit_combo.current(0)
        price_entry.delete(0, tk.END)

        # Обновляем таблицу
        load_materials()

        print("Материал добавлен")

    except Exception as e:
        print("Ошибка:", e)

def load_materials():

    for row in tree.get_children():
        tree.delete(row)

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT material_id,
               material_name,
               unit,
               price
        FROM material
        ORDER BY material_id
    """

    cursor.execute(query)

    rows = cursor.fetchall()
  
    for row in rows:
        tree.insert("", tk.END, values=row)

    cursor.close()
    conn.close()


root = tk.Tk()

root.title("Мебельное производство")
root.geometry("800x500")


title_label = tk.Label(
    root,
    text="Справочник материалов",
    font=("Arial", 16)
)

title_label.pack(pady=10)


columns = ("ID", "Название", "Ед.", "Цена")

tree = ttk.Treeview(
    root,
    columns=columns,
    show="headings"
)

for col in columns:
    tree.heading(col, text=col)

tree.column("ID", width=50)
tree.column("Название", width=300)
tree.column("Ед.", width=100)
tree.column("Цена", width=100)

tree.pack(fill="both", expand=True, padx=10, pady=10)


refresh_button = tk.Button(
    root,
    text="Обновить данные",
    command=load_materials
)

refresh_button.pack(pady=10)

#-
# Форма добавления материала
#-

form_frame = tk.Frame(root)
form_frame.pack(pady=10)

# Название
name_label = tk.Label(form_frame, text="Название")
name_label.grid(row=0, column=0, padx=5)

name_entry = tk.Entry(form_frame)
name_entry.grid(row=0, column=1, padx=5)

# Единица измерения
unit_label = tk.Label(form_frame, text="Ед.")
unit_label.grid(row=0, column=2, padx=5)


unit_combo = ttk.Combobox(
    form_frame,
    values=["шт", "м", "кв.м", "л", "кг"],
    state="readonly"
)

unit_combo.grid(row=0, column=3, padx=5)

# Значение по умолчанию
unit_combo.current(0)

# Цена
price_label = tk.Label(form_frame, text="Цена")
price_label.grid(row=0, column=4, padx=5)

price_entry = tk.Entry(form_frame)
price_entry.grid(row=0, column=5, padx=5)


load_materials()

# Кнопка добавления
add_button = tk.Button(
    root,
    text="Добавить материал",
    command=add_material
)

add_button.pack(pady=10)

root.mainloop()