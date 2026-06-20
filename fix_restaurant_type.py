import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Load credentials from .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    sys.exit(1)

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Connected to Supabase\n")

# STEP 1: Show transactions BEFORE fix
print("="*80)
print("STEP 1: FINDING RESTAURANT TRANSACTIONS WITH WRONG TYPE")
print("="*80)

restaurant_merchants = ["Suresh Krishana", "KULANTHAIVELU PURUS"]

try:
    response = supabase.table("transactions").select("*").in_("merchant_name", restaurant_merchants).eq("type", "Income").execute()
    before_transactions = response.data

    if not before_transactions:
        print("\n✨ No restaurant transactions with type='Income' found!")
        print("Issue 4 is already fixed or doesn't exist.")
        sys.exit(0)

    print(f"\n🔴 Found {len(before_transactions)} transactions to fix:\n")

    for i, txn in enumerate(before_transactions, 1):
        print(f"{i}. ID: {txn['id']}")
        print(f"   Merchant: {txn['merchant_name']}")
        print(f"   Amount: ₹{txn['amount']}")
        print(f"   Date: {txn['timestamp']}")
        print(f"   Current Type: {txn['type']} (WRONG)")
        print(f"   Current Category: {txn['category']}")
        print()

except Exception as e:
    print(f"❌ Error fetching transactions: {e}")
    sys.exit(1)

# STEP 2: Ask for confirmation
print("="*80)
print("STEP 2: CONFIRMATION")
print("="*80)
print("\n⚠️  About to change:")
print("   - Merchants: Suresh Krishana, KULANTHAIVELU PURUS")
print("   - type: 'Income' → 'Expenses'")
print("   - category: (current) → 'Food Outside'")
print()

confirm = input("Proceed with update? (y/n): ").strip().lower()
if confirm != 'y':
    print("❌ Cancelled. No changes made.")
    sys.exit(0)

# STEP 3: Run the UPDATE
print("\n" + "="*80)
print("STEP 3: EXECUTING UPDATE")
print("="*80)

try:
    # Get all transaction IDs to update
    transaction_ids = [txn['id'] for txn in before_transactions]

    # Update each transaction
    for txn_id in transaction_ids:
        supabase.table("transactions").update({
            "type": "Expenses",
            "category": "Food Outside"
        }).eq("id", txn_id).execute()

    print(f"\n✅ Updated {len(transaction_ids)} transactions successfully!")

except Exception as e:
    print(f"❌ Error updating transactions: {e}")
    sys.exit(1)

# STEP 4: Show transactions AFTER fix
print("\n" + "="*80)
print("STEP 4: VERIFYING CHANGES (AFTER)")
print("="*80)

try:
    response = supabase.table("transactions").select("*").in_("merchant_name", restaurant_merchants).execute()
    after_transactions = response.data

    print(f"\n✅ All restaurant transactions after fix:\n")

    for i, txn in enumerate(after_transactions, 1):
        print(f"{i}. ID: {txn['id']}")
        print(f"   Merchant: {txn['merchant_name']}")
        print(f"   Amount: ₹{txn['amount']}")
        print(f"   Date: {txn['timestamp']}")
        print(f"   Type: {txn['type']} ✅ (FIXED)")
        print(f"   Category: {txn['category']} ✅ (FIXED)")
        print()

except Exception as e:
    print(f"❌ Error verifying changes: {e}")
    sys.exit(1)

# STEP 5: Summary
print("="*80)
print("SUMMARY")
print("="*80)
print(f"✅ Fixed {len(before_transactions)} restaurant transactions")
print(f"   - Merchants: {', '.join(restaurant_merchants)}")
print(f"   - Changed type: Income → Expenses")
print(f"   - Changed category: (various) → Food Outside")
print(f"✅ All changes committed to Supabase")
print("="*80)
