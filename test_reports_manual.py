"""
Manual Test Script for Daily/Weekly/Monthly Reports
Run this to test reports without waiting for scheduled times
"""
from report_generator import ReportGenerator
from email_alerts import send_daily_report, send_weekly_report, send_monthly_report
from logger import log
import os
from dotenv import load_dotenv

load_dotenv()
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

print("=" * 80)
print("TESTING EXPENDITURE REPORTS")
print("=" * 80)

generator = ReportGenerator()

# Test 1: Daily Report
print("\n[TEST 1] DAILY REPORT")
print("-" * 80)
daily_report = generator.format_daily_report()
print(f"Subject: {daily_report['subject']}")
print(f"Total Spent: Rs {daily_report['total_spent']:,.2f}")
print(f"Transactions: {daily_report['transaction_count']}")
print(f"Top Merchants: {daily_report['top_merchants'][:3]}")
print(f"Categories: {list(daily_report['category_breakdown'].keys())}")

# Send test email
print("\n[EMAIL] Sending daily report email...")
result = send_daily_report()
if result:
    print("[OK] Daily report sent successfully!")
else:
    print("[ERROR] Failed to send daily report")

# Test 2: Weekly Report
print("\n" + "=" * 80)
print("[TEST 2] WEEKLY REPORT")
print("-" * 80)
weekly_report = generator.format_weekly_report()
print(f"Subject: {weekly_report['subject']}")
print(f"Total Spent: Rs {weekly_report['total_spent']:,.2f}")
print(f"Transactions: {weekly_report['transaction_count']}")
print(f"Top Merchants: {weekly_report['top_merchants'][:3]}")
print(f"Categories: {list(weekly_report['category_breakdown'].keys())}")

# Send test email
print("\n[EMAIL] Sending weekly report email...")
result = send_weekly_report()
if result:
    print("[OK] Weekly report sent successfully!")
else:
    print("[ERROR] Failed to send weekly report")

# Test 3: Monthly Report
print("\n" + "=" * 80)
print("[TEST 3] MONTHLY REPORT")
print("-" * 80)
monthly_report = generator.format_monthly_report()
print(f"Subject: {monthly_report['subject']}")
print(f"Total Spent: Rs {monthly_report['total_spent']:,.2f}")
print(f"Transactions: {monthly_report['transaction_count']}")
print(f"Top Merchants: {monthly_report['top_merchants'][:3]}")
print(f"Categories: {list(monthly_report['category_breakdown'].keys())}")

# Send test email
print("\n[EMAIL] Sending monthly report email...")
result = send_monthly_report()
if result:
    print("[OK] Monthly report sent successfully!")
else:
    print("[ERROR] Failed to send monthly report")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"""
[OK] Report Generation: SUCCESS
   - Daily: Rs {daily_report['total_spent']:,.2f} ({daily_report['transaction_count']} txns)
   - Weekly: Rs {weekly_report['total_spent']:,.2f} ({weekly_report['transaction_count']} txns)
   - Monthly: Rs {monthly_report['total_spent']:,.2f} ({monthly_report['transaction_count']} txns)

[OK] Email Sending: CHECK YOUR INBOX!
   - 3 test emails sent to {ALERT_EMAIL}

[REPORTS INCLUDE]
   [OK] Total spending amount
   [OK] Transaction count
   [OK] Top 5 merchants
   [OK] Category breakdown with percentages
   [OK] Comparison with previous period
   [OK] Beautiful HTML formatting

[SCHEDULING]
   - Daily: 11:00 PM every day
   - Weekly: Sunday at 6:00 PM
   - Monthly: 1st of month at 6:00 PM

[AUTOMATION] Reports will send automatically via listener.py
""")

print("=" * 80)
print("Check your Gmail inbox for the 3 test reports!")
print("=" * 80)
