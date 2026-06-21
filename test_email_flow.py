from sync_engine import SyncEngine

# Test SMS
test_sms = {
    "sms_body": "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/987654321/AMAZON PAY",
    "sender": "AXISBK",
}

print("=" * 80)
print("TESTING EMAIL ALERTS WITH TEST SMS")
print("=" * 80)

engine = SyncEngine()

# Process the test SMS (without sms_id to avoid UUID validation)
print(f"\n📱 Processing SMS from {test_sms['sender']}")
print(f"Body: {test_sms['sms_body'][:50]}...")

result = engine.process_sms(test_sms['sms_body'], sms_id=None)

if result:
    print("\n✅ SMS processed successfully!")
    print(f"   Merchant: {result['merchant_name']}")
    print(f"   Amount: ₹{result['amount']}")
    print(f"   Category: {result['category']}")
    print(f"   Type: {result['type']}")
    print("\n📧 Email alert should have been sent!")
else:
    print("\n❌ SMS processing failed")

print("=" * 80)
print("Check your Gmail inbox for the alert email")
print("=" * 80)
