"""Tkinter implementation of the converter view contract."""

import tkinter as tk
from tkinter import filedialog, messagebox

APP_TITLE = "ANZ to RentHQ OFX Converter"


class TkinterConverterView:
    def __init__(self):
        root = tk.Tk()
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        title = tk.Label(
            root,
            text="ANZ Excel → RentHQ OFX Converter",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=15)
        self.info_label = tk.Label(
            root,
            text="Select an ANZ Excel file (.xlsx)",
            fg="navy"

        )
        self.info_label.pack(pady=5)
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        self.browse_btn = tk.Button(
            btn_frame,
            text="Browse Excel File",
            width=20,
            height=2,
        )
        self.browse_btn.pack(side=tk.LEFT, padx=10)
        self.convert_btn = tk.Button(
            btn_frame,
            text="Convert to OFX",
            width=20,
            height=2,
        )
        self.convert_btn.pack(side=tk.LEFT, padx=10)
        self.file_label = tk.Label(
            root,
            text="No file selected",
            wraplength=550
        )
        self.file_label.pack(pady=10)
        help_text = (
            "Required columns:\n"
            "Transaction Date | Details | Reference | Amount"

        )
        tk.Label(
            root,
            text=help_text,
            fg="gray"
        ).pack(pady=10)

    def bind_actions(self, select_file, convert_file):
        self.browse_btn.config(command=select_file)
        self.convert_btn.config(command=convert_file)

    def choose_excel_file(self):
        return filedialog.askopenfilename(
            title="Select ANZ Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls")],
        )

    def show_selected_file(self, filename):
        self.file_label.config(text=f"Selected:\n{filename}")
        self.info_label.config(text="Ready to convert")

    def show_warning(self, title, message):
        messagebox.showwarning(title, message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def run(self):
        self.root.mainloop()
