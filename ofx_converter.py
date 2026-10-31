import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from pathlib import Path
from datetime import datetime
import traceback
APP_TITLE = "ANZ to RentHQ OFX Converter"

class OFXConverterService:
    def create_fitid(self, date_value, amount, row_number):
        amount_part = str(abs(amount)).replace(".", "")
        return (
            f"{date_value.strftime('%Y%m%d')}"
            f"{amount_part}"
            f"{row_number}"
        )
        
    def build_transactions(self, df):
        transactions = []
        count = 0
        dates = []
        for idx, row in df.iterrows():
            date_value = pd.to_datetime(
                row["Transaction Date"],
                dayfirst=True
            )
            dates.append(date_value)
            amount = float(row["Amount"])
            details = str(
                row["Details"]
            ).strip()
            reference = str(
                row["Reference"]
            ).strip()
            fitid = self.create_fitid(
                date_value,
                amount,
                idx + 1
            )
            trntype = (
                "DEP"
                if amount >= 0
                else "PAYMENT"
            )
            transaction = f"""
<STMTTRN>
<TRNTYPE>{trntype}

<DTPOSTED>{date_value.strftime('%Y%m%d')}000000
<TRNAMT>{amount:.2f}
<FITID>{fitid}
<NAME>{details}
<MEMO>{reference}
</STMTTRN>
"""
            transactions.append(transaction)
            count += 1
        return (
            "\n".join(transactions),
            min(dates),
            max(dates),
            count
        )
        
    def build_ofx(self, df):
        transactions, start_date, end_date, count = (
            self.build_transactions(df)
        )
        now = datetime.now()
        ofx = f"""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<SIGNONMSGSRSV1>
<SONRS>
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<DTSERVER>{now.strftime('%Y%m%d%H%M%S')}
<LANGUAGE>ENG
</SONRS>
</SIGNONMSGSRSV1>
<BANKMSGSRSV1>
<STMTTRNRS>
<TRNUID>1
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<STMTRS>
<CURDEF>NZD
<BANKACCTFROM>
<ACCTTYPE>CHECKING
</BANKACCTFROM>
<BANKTRANLIST>
<DTSTART>{start_date.strftime('%Y%m%d')}
<DTEND>{end_date.strftime('%Y%m%d')}
{transactions}
</BANKTRANLIST>
<LEDGERBAL>

<BALAMT>0.00
<DTASOF>{end_date.strftime('%Y%m%d')}
</LEDGERBAL>
<AVAILBAL>
<BALAMT>0.00
<DTASOF>{end_date.strftime('%Y%m%d')}
</AVAILBAL>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>
"""
        return ofx, count

    def convert_file(self, excel_file):
        """Convert an Excel file and return its OFX path and transaction count."""
        df = pd.read_excel(
            excel_file
        )
        required_columns = [
            "Transaction Date",
            "Details",
            "Reference",
            "Amount"

        ]
        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]
        if missing:
            raise Exception(
                "Missing columns:\n\n"
                + "\n".join(missing)
            )
        ofx_text, count = self.build_ofx(df)
        source_path = Path(
            excel_file
        )
        output_file = (
            source_path.parent
            / f"{source_path.stem}.ofx"
        )
        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(ofx_text)
        return output_file, count


class OFXConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("600x300")
        self.root.resizable(False, False)
        self.selected_file = None
        self.service = OFXConverterService()
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
