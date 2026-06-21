import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from logger import log

load_dotenv()

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

def send_transaction_alert(merchant_name, amount, category,transaction_type):
    try:
        subject = f"Transaction Alert: {merchant_name}"

        body = f"""Transaction Processed:

        Merchant: {merchant_name}
        Amount: ₹{amount}
        Category: {category}
        Type: {transaction_type}

        Your SMS Budget Tracker
        """
        
        msg = MIMEMultipart()
        msg["From"] = GMAIL_EMAIL
        msg["To"] = ALERT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            server.sendmail(GMAIL_EMAIL, ALERT_EMAIL, msg.as_string())
        
        log.info(f"✅ Email alert sent: {merchant_name} - ₹{amount}")
        return True
    except Exception as e:
        log.error(f"❌ Failed to send email alert: {e}")
        return False
    

def send_error_alert(error_type, error_message, sms_id):
    """Send email alert for parse/processing errors"""
    try:
        subject = f"🚨 SMS Processing Error"
        
        body = f"""
Error occurred while processing SMS:

Error Type: {error_type}
Message: {error_message}
SMS ID: {sms_id}

Check dashboard for details.

Your SMS Budget Tracker
        """
        
        msg = MIMEMultipart()
        msg["From"] = GMAIL_EMAIL
        msg["To"] = ALERT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            server.sendmail(GMAIL_EMAIL, ALERT_EMAIL, msg.as_string())
        
        log.info(f"✅ Error alert sent for SMS {sms_id}")
        return True
        
    except Exception as e:
        log.error(f"❌ Error alert failed: {e}")
        return False
    

def send_daily_summary(total_expenses, total_income, transaction_count, top_category):
    """Send daily spending summary email"""
    try:
        subject = f"📊 Daily Budget Summary"
        
        body = f"""
Daily Spending Summary:

Total Expenses: ₹{total_expenses}
Total Income: ₹{total_income}
Transactions: {transaction_count}
Top Category: {top_category}

Your SMS Budget Tracker
        """
        
        msg = MIMEMultipart()
        msg["From"] = GMAIL_EMAIL
        msg["To"] = ALERT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
            server.sendmail(GMAIL_EMAIL, ALERT_EMAIL, msg.as_string())
        
        log.info(f"✅ Daily summary sent")
        return True
        
    except Exception as e:
        log.error(f"❌ Daily summary failed: {e}")
        return False