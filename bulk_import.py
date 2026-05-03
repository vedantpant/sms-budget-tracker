import json
from parser import process_sms
from openpyxl_basic import add_bulk_to_excel

with open("all_sms.json", "r", encoding="utf-8") as f:
    all_sms = json.load(f)

axis_sms = [sms for sms in all_sms if "AXISBK" in sms["address"]]
print(f"Total Axis SMS: {len(axis_sms)}")

transactions = []
for sms in axis_sms:
    transaction = process_sms(sms["body"])
    if transaction:
        transactions.append(transaction)
    else:
        print(f"Skipped: {sms['body'][:50]}")

print(f"\nParsed {len(transactions)} transactions — adding to Excel...")
add_bulk_to_excel(transactions)