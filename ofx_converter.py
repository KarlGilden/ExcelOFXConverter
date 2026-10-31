import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import traceback

from services.excel_ofx_converter import ExcelOFXConverter

APP_TITLE = "ANZ to RentHQ OFX Converter"

class OFXConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        self.selected_file = None
        self.service = ExcelOFXConverter()
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
        browse_btn = tk.Button(
            btn_frame,
            text="Browse Excel File",
            width=20,
            height=2,
            command=self.select_file
        )
        browse_btn.pack(side=tk.LEFT, padx=10)
        convert_btn = tk.Button(
            btn_frame,
            text="Convert to OFX",
            width=20,
            height=2,
            command=self.convert_file
        )
        convert_btn.pack(side=tk.LEFT, padx=10)
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
        
    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Select ANZ Excel File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls")
            ]
        )
        if filename:
            self.selected_file = filename
            self.file_label.config(
                text=f"Selected:\n{filename}"
            )
            self.info_label.config(
                text="Ready to convert"
            )
            
    def convert_file(self):
        try:
            if not self.selected_file:
                messagebox.showwarning(
                    "No File Selected",
                    "Please select an Excel file first."
                )
                return
            output_file, count = self.service.convert_file(self.selected_file)
            messagebox.showinfo(
                "Conversion Successful",
                f"Transactions Imported: {count}\n\n"
                f"OFX File Created:\n\n"

                f"{output_file}"
            )
        except Exception as ex:
            log_file = (
                Path.home()
                / "anz_ofx_error.log"
            )
            with open(
                log_file,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(
                    traceback.format_exc()
                )
            messagebox.showerror(
                "Conversion Error",
                str(ex)
            )
def main():
    root = tk.Tk()
    OFXConverterGUI(root)
    root.mainloop()
if __name__ == "__main__":
    main()
