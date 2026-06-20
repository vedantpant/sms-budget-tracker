import json
from sync_engine import SyncEngine

engine = SyncEngine()

with open("all_sms.json", "r", encoding="utf-8") as f:
    all_sms = json.load(f)

axis_sms = [sms for sms in all_sms if "AXISBK" in sms["address"]]
print(f"Total Axis SMS: {len(axis_sms)}")

success, skipped, failed = 0, 0, 0

for sms in axis_sms:
    try:
        result = engine.process_sms(sms["body"], sms_id=None)
        if result:
            success += 1
            print(f"✅ {result['merchant_name']} ₹{result['amount']}")
        else:
            skipped += 1
    except Exception as e:
        if "Duplicate" in str(e):
            skipped += 1
        else:
            print(f"❌ Failed: {e}")
            failed += 1

print(f"\nDone! ✅{success} added, ⏭️{skipped} skipped, ❌{failed} failed")