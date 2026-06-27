"""
Test Bank Reconciliation
Shows how to use the CSV reconciliation feature
"""
from bank_reconciliation_csv import CSVBankReconciliation
import json


def test_reconciliation():
    """
    Test reconciliation with the bank statement

    Steps:
    1. Export bank statement as CSV (copy/paste table from PDF to Excel)
    2. Save as "bank_statement.csv"
    3. Run this test
    """

    # Initialize reconciliation
    reconciler = CSVBankReconciliation()

    # You can reconcile a CSV file like this:
    # result = reconciler.reconcile_csv("bank_statement.csv")

    # For now, let's show the expected format:
    print("=" * 60)
    print("BANK RECONCILIATION GUIDE")
    print("=" * 60)
    print()
    print("Step 1: Export Bank Statement as CSV")
    print("-" * 60)
    print("Option A - Manual Export:")
    print("  1. Open the PDF in your browser")
    print("  2. Select the transaction table")
    print("  3. Copy and paste into Excel")
    print("  4. Save as 'bank_statement.csv'")
    print()
    print("Option B - Use Python:")
    print("  1. Copy bank transactions to bank_statement.csv")
    print("  2. Expected columns:")
    print("     - Date (DD-MM-YYYY)")
    print("     - Transaction Details")
    print("     - Withdrawal (for debits)")
    print("     - Deposits (for credits)")
    print()
    print("Step 2: Run Reconciliation")
    print("-" * 60)
    print("Python code:")
    print("  from bank_reconciliation_csv import CSVBankReconciliation")
    print("  reconciler = CSVBankReconciliation()")
    print("  result = reconciler.reconcile_csv('bank_statement.csv')")
    print("  print(json.dumps(result, indent=2))")
    print()
    print("=" * 60)
    print()

    # Check if CSV exists
    import os
    csv_path = "bank_statement.csv"

    if os.path.exists(csv_path):
        print(f"Found {csv_path}! Running reconciliation...")
        print("-" * 60)
        result = reconciler.reconcile_csv(csv_path)
        print(json.dumps(result, indent=2))
    else:
        print(f"CSV file '{csv_path}' not found.")
        print("Create one using the steps above.")


if __name__ == "__main__":
    test_reconciliation()
