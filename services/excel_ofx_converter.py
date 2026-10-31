from datetime import datetime
from pathlib import Path

import pandas as pd


class ExcelOFXConverter:
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
