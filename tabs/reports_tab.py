import tkinter as tk
from tkinter import ttk

from reports.product_cost_report import product_cost_report
from reports.techprocess_report import tech_process_report
from reports.material_usage_report import material_usage_report



def create_reports_tab(notebook):

    tab = tk.Frame(notebook)
    notebook.add(tab, text="Отчеты")


    title = tk.Label(
        tab,
        text="Отчеты",
        font=("Arial", 18)
    )

    title.pack(pady=10)


    report_tree = ttk.Treeview(tab)
    report_tree.pack(fill="both", expand=True, padx=10, pady=10)


    button_frame = tk.Frame(tab)
    button_frame.pack(pady=10)


    tk.Button(
        button_frame,
        text="Себестоимость изделий",
        width=30,
        command=lambda: product_cost_report(report_tree)
    ).grid(row=0, column=0, padx=5)


    tk.Button(
        button_frame,
        text="Техпроцесс",
        width=30,
        command=lambda: tech_process_report(report_tree)
    ).grid(row=0, column=1, padx=5)


    tk.Button(
        button_frame,
        text="Использование материалов",
        width=30,
        command=lambda: material_usage_report(report_tree)
    ).grid(row=0, column=2, padx=5)