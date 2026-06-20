from supabase_client import SupabaseClient
from openpyxl_basic import add_to_excel

db = SupabaseClient()

# Supabase se woh transactions fetch karo jo May 3 se hain
response = db.client.table('transactions')\
    .select('*')\
    .gte('timestamp', '2026-05-03')\
    .execute()

transactions = response.data
print(f"Total transactions to sync: {len(transactions)}")

success, skipped = 0, 0

for txn in transactions:
    try:
        # timestamp format convert karo
        from datetime import datetime
        dt = datetime.fromisoformat(txn['timestamp'].replace('+00:00', ''))
        raw_ts = dt.strftime("%d-%m-%y, %H:%M:%S")
        
        add_to_excel({
            'amount': txn['amount'],
            'type': txn['type'],
            'category': txn['category'],
            'merchant_name': txn['merchant_name'],
            'transaction_id': txn['transaction_id'],
            'timestamp': raw_ts
        })
        success += 1
    except Exception as e:
        print(f"❌ Failed: {txn['merchant_name']} - {e}")

print(f"\nDone! ✅{success} synced")