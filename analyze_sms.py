import json
import re

with open("all_sms.json", "r", encoding="utf-8") as f:
    sms_data = json.load(f)

# Filter AXISBK SMS
axisbk_sms = [sms for sms in sms_data if "AXISBK" in sms.get("address", "")]

print(f"Total AXISBK SMS: {len(axisbk_sms)}\n")

# Categorize by format
formats = {
    "upi_debit": [],
    "outward_rem": [],
    "credit_with_on": [],
    "credit_without_on": [],
    "credit_upi": [],
    "ach_credit": [],
    "ach_debit": [],
    "nach_debit": [],
    "google_play": [],
    "auto_pay": [],
    "other": []
}

for sms in axisbk_sms:
    body = sms.get("body", "")

    if "debited" in body and "UPI/P2" in body:
        formats["upi_debit"].append(body)
    elif "OUTWARD REM" in body:
        formats["outward_rem"].append(body)
    elif "credited" in body and "by" in body and "VPA" in body:
        formats["credit_upi"].append(body)
    elif "credited" in body and ("ACH-CR" in body or "Info -" in body or "Ref:" in body):
        if " on " in body:
            formats["credit_with_on"].append(body)
        else:
            formats["credit_without_on"].append(body)
    elif "Debit" in body and "ACH-DR" in body:
        formats["ach_debit"].append(body)
    elif "NACH debit" in body:
        formats["nach_debit"].append(body)
    elif "Google Play" in body or "GOOGLEPLAY" in body:
        formats["google_play"].append(body)
    elif "Auto Pay" in body:
        formats["auto_pay"].append(body)
    else:
        formats["other"].append(body)

# Print summary
print("="*80)
print("QUICK SUMMARY")
print("="*80)

for fmt, examples in formats.items():
    if examples:
        print(f"\n{fmt.upper()}: {len(examples)} SMS")
        if examples:
            preview = examples[0][:100].replace("\n", " ")
            print(f"  Preview: {preview}...")

print("\n" + "="*80)
print("DETAILED BREAKDOWN (showing 2 examples per format)")
print("="*80)

# Show examples of each type
for fmt, examples in formats.items():
    if examples:
        print(f"\n\n### {fmt.upper()} (Count: {len(examples)}) ###\n")
        for i, example in enumerate(examples[:2], 1):
            print(f"--- Example {i} ---")
            print(example)
            print()
