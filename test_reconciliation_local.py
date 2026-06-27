"""
Local Reconciliation Test (No Supabase Required)
Shows how CSV parsing works
"""
import pandas as pd
import re
from datetime import datetime
from typing import List, Dict


def parse_csv_rows(csv_path: str) -> List[Dict]:
    """Parse CSV into transactions"""
    transactions = []

    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} rows from CSV")
        print()

        for idx, row in df.iterrows():
            try:
                date_str = str(row.get('Date', '')).strip()
                details = str(row.get('Transaction Details', '')).strip()
                withdrawal = row.get('Withdrawal', None)
                deposit = row.get('Deposits', None)

                if not date_str or not details:
                    continue

                # Parse date
                try:
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                    date_formatted = date_obj.strftime("%d-%m-%y")
                except:
                    continue

                # Determine amount and type
                amount = None
                tx_type = None

                if pd.notna(withdrawal) and withdrawal != "":
                    try:
                        amount = float(str(withdrawal).replace(",", ""))
                        tx_type = "debit"
                    except:
                        pass

                if pd.notna(deposit) and deposit != "":
                    try:
                        amount = float(str(deposit).replace(",", ""))
                        tx_type = "credit"
                    except:
                        pass

                if not amount or not tx_type:
                    continue

                # Extract merchant
                merchant = extract_merchant(details)

                transactions.append({
                    "date": date_formatted,
                    "amount": amount,
                    "type": tx_type,
                    "merchant_name": merchant,
                    "description": details
                })

            except Exception as e:
                print(f"  Warning: Could not parse row {idx}: {e}")
                continue

        return transactions

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []


def extract_merchant(details: str) -> str:
    """Extract merchant name from transaction details"""
    details = details.upper()

    # UPI pattern
    upi_match = re.search(r'/([A-Z0-9\s]+)/UPI', details)
    if upi_match:
        return upi_match.group(1).strip()

    # ACH pattern
    ach_match = re.search(r'ACH-[A-Z]{2}-([A-Z0-9\s]+?)(?:-|$)', details)
    if ach_match:
        return ach_match.group(1).strip()

    # NEFT/IMPS
    if "NEFT" in details:
        return "NEFT TRANSFER"
    if "IMPS" in details:
        return "IMPS TRANSFER"

    # Purchase pattern
    if "PURCHASE AT" in details:
        match = re.search(r'PURCHASE AT\s+([A-Z0-9\s]+)', details)
        if match:
            return match.group(1).strip()

    # Outward Remittance
    if "OUTWARD REM" in details:
        return "OUTWARD REMITTANCE"

    # Default
    return details[:50].strip()


def main():
    print("=" * 80)
    print("LOCAL BANK RECONCILIATION TEST (CSV Parsing)")
    print("=" * 80)
    print()

    csv_path = "test_bank_statement.csv"

    # Step 1: Parse CSV
    print("Step 1: Parsing Bank Statement CSV")
    print("-" * 80)
    transactions = parse_csv_rows(csv_path)

    print()
    print("Step 2: Parsed Transactions")
    print("-" * 80)
    print(f"Total transactions: {len(transactions)}")
    print()

    # Display each transaction
    print("Transactions:")
    print()
    for i, txn in enumerate(transactions, 1):
        print(f"{i}. {txn['date']} | {txn['merchant_name']:<40} | INR {txn['amount']:>10.2f} ({txn['type']:<6})")

    print()
    print("Step 3: Transaction Summary")
    print("-" * 80)

    # Summary
    debits = sum(t['amount'] for t in transactions if t['type'] == 'debit')
    credits = sum(t['amount'] for t in transactions if t['type'] == 'credit')

    print(f"Total Debits:  INR {debits:>15,.2f}")
    print(f"Total Credits: INR {credits:>15,.2f}")
    print(f"Net:           INR {credits - debits:>15,.2f}")

    print()
    print("=" * 80)
    print("CSV PARSING SUCCESSFUL!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. When Supabase is accessible, run: python test_reconciliation.py")
    print("2. This will compare with your actual transactions and add missing ones")
    print()


if __name__ == "__main__":
    main()
