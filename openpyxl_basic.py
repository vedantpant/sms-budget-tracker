from datetime import datetime
import time
from win32com.client import Dispatch

FILE_PATH = r"D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\Ultimate Personal Budget Manager.xlsx"

def get_existing_transactions(ws):
    existing_ids = set()    # UPI transaction IDs
    existing_keys = set()   # date+amount+merchant for non-UPI

    last_row = ws.Cells(ws.Rows.Count, 4).End(-4162).Row
    for row in range(12, last_row + 1):
        date = ws.Cells(row, 3).Value
        amount = ws.Cells(row, 6).Value
        details = ws.Cells(row, 7).Value
        if not details:
            continue
        if "|" in str(details):
            parts = str(details).split("|")
            if len(parts) >= 2:
                identifier = parts[1].strip()
                existing_ids.add(identifier)
        else:
            date_str = str(date).split(" ")[0] if date else ""
            key = f"{date_str}_{amount}_{details}"
            existing_keys.add(key)

    return existing_ids, existing_keys


def add_bulk_to_excel(transactions):
    excel = Dispatch("Excel.Application")
    wb = excel.Workbooks.Open(FILE_PATH)
    ws = wb.Sheets("Budget Tracking")

    existing_ids, existing_keys = get_existing_transactions(ws)
    print(f"Existing transactions in Excel: {len(existing_ids) + len(existing_keys)}")

    added = 0
    skipped = 0

    for transaction in transactions:
        # duplicate check
        txn_id = transaction["transaction_id"]
        date_str = transaction["timestamp"].split(",")[0].strip()
        dt = datetime.strptime(date_str, "%d-%m-%y")
        date_key = dt.strftime("%d-%m-%Y")
        time_str = transaction["timestamp"].split(",")[1].strip() if "," in transaction["timestamp"] else ""
        fallback_key = f"{date_key}_{time_str}_{transaction['amount']}_{transaction['merchant_name']}"
        

        if txn_id and txn_id in existing_ids:
            print(f"⏭️ Duplicate skipped: {transaction['merchant_name']} — ₹{transaction['amount']}")
            skipped += 1
            continue
        elif not txn_id and fallback_key in existing_keys:
            print(f"⏭️ Duplicate skipped: {transaction['merchant_name']} — ₹{transaction['amount']}")
            skipped += 1
            continue

        # last row aur balance fetch karo
        last_row = ws.Cells(ws.Rows.Count, 4).End(-4162).Row
        if last_row <= 11:
            last_balance = 0.0
            new_row = 12
        else:
            if ws.Cells(last_row, 4).Value is None:
                new_row = last_row
            else:
                new_row = last_row + 1
            last_balance = None
            check_row = last_row
            while last_balance is None and check_row > 11:
                val = ws.Cells(check_row, 8).Value
                if val is not None:
                    last_balance = float(val)
                check_row -= 1
            if last_balance is None:
                last_balance = 0.0

        amount = float(transaction["amount"])
        new_balance = last_balance + amount if transaction["type"] == "Income" else last_balance - amount

        # details column — merchant | txn_id
        if txn_id:
            details = f"{transaction['merchant_name']} | {txn_id}"
        else:
            time_str = transaction["timestamp"].split(",")[1].strip() if "," in transaction["timestamp"] else ""
            details = f"{transaction['merchant_name']} | {date_key} {time_str}"

        ws.Cells(new_row, 3).Value = dt
        ws.Cells(new_row, 4).Value = transaction["type"]
        ws.Cells(new_row, 5).Value = transaction["category"]
        ws.Cells(new_row, 6).Value = amount
        ws.Cells(new_row, 7).Value = details
        ws.Cells(new_row, 8).Value = new_balance
        ws.Cells(new_row, 9).Value = dt

        # set mein add karo
        if txn_id:
            existing_ids.add(txn_id)
        else:
            existing_keys.add(fallback_key)

        added += 1
        print(f"✅ {transaction['merchant_name']} — ₹{transaction['amount']}")

    wb.Close(SaveChanges=True)
    excel.Quit()
    print(f"\nDone! Added: {added}, Skipped: {skipped}")


def add_to_excel(transaction):
    add_bulk_to_excel([transaction])


if __name__ == "__main__":
    test_transaction = {
        "amount": "645.00",
        "type": "Expenses",
        "category": "Food Outside",
        "merchant_name": "CALIFORNIA BURRITO",
        "transaction_id": "502760971106",
        "timestamp": "25-04-26, 19:30:00"
    }
    add_to_excel(test_transaction)