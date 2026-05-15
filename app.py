import tkinter as tk
from tkinter import ttk

from tabs.materials_tab import create_materials_tab
from tabs.products_tab import create_products_tab
from tabs.reports_tab import create_reports_tab


root = tk.Tk()
root.title("Мебельное производство")
root.geometry("1400x800")


notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)


create_materials_tab(notebook)
create_products_tab(notebook)
create_reports_tab(notebook)


root.mainloop()