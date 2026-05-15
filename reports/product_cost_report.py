from database.db import connect_db
import tkinter as tk



def product_cost_report(tree):

    for row in tree.get_children():
        tree.delete(row)


    tree["columns"] = (
        "Изделие",
        "Кол-во",
        "Себестоимость",
        "Цена",
        "Прибыль"
    )

    tree["show"] = "headings"


    for col in tree["columns"]:
        tree.heading(col, text=col)


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