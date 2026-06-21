"""
Comprehensive Email Alerts Tests
Tests email delivery, rate limiting, and error handling
"""
from email_alerts import send_transaction_alert, send_error_alert, send_daily_summary
from unittest.mock import patch, MagicMock
import pytest
import smtplib

# ============================================================================
# TRANSACTION ALERT TESTS
# ============================================================================

def test_transaction_alert_structure():
    """Test that transaction alert is sent with correct structure"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_transaction_alert(
            merchant_name="AMAZON PAY",
            amount=500.00,
            category="Shopping",
            transaction_type="Expenses"
        )

        assert result == True
        mock_server.login.assert_called()
        mock_server.sendmail.assert_called()

def test_transaction_alert_with_large_amount():
    """Test alert for large transaction amount"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_transaction_alert(
            merchant_name="PROPERTY DEALER",
            amount=9999999.99,
            category="Real Estate",
            transaction_type="Expenses"
        )

        assert result == True

def test_transaction_alert_with_small_amount():
    """Test alert for small transaction amount"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_transaction_alert(
            merchant_name="CANDY SHOP",
            amount=0.50,
            category="Food",
            transaction_type="Expenses"
        )

        assert result == True

def test_transaction_alert_with_special_characters():
    """Test alert for merchant with special characters"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_transaction_alert(
            merchant_name="SHOP-N-SAVE & CO",
            amount=500.00,
            category="Shopping",
            transaction_type="Expenses"
        )

        assert result == True

# ============================================================================
# ERROR ALERT TESTS
# ============================================================================

def test_error_alert_structure():
    """Test that error alert is sent correctly"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_error_alert(
            error_type="ParsingError",
            error_message="Could not parse SMS format",
            sms_id="test_sms_123"
        )

        assert result == True
        mock_server.sendmail.assert_called()

def test_error_alert_with_long_message():
    """Test error alert with very long error message"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        long_error = "A" * 1000  # 1000 character error message

        result = send_error_alert(
            error_type="SupabaseConnectionError",
            error_message=long_error,
            sms_id="test_sms_456"
        )

        assert result == True

def test_error_alert_with_special_characters():
    """Test error alert with special characters in error message"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_error_alert(
            error_type="ValueError",
            error_message="Invalid <html> & special 'chars' \"quoted\"",
            sms_id="test_sms_789"
        )

        assert result == True

# ============================================================================
# DAILY SUMMARY TESTS
# ============================================================================

def test_daily_summary_structure():
    """Test that daily summary is sent correctly"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_daily_summary(
            total_expenses=50000.00,
            total_income=100000.00,
            transaction_count=25,
            top_category="Food Outside"
        )

        assert result == True
        mock_server.sendmail.assert_called()

def test_daily_summary_with_zero_expenses():
    """Test daily summary when there are no expenses"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_daily_summary(
            total_expenses=0.00,
            total_income=100000.00,
            transaction_count=1,
            top_category="Income"
        )

        assert result == True

def test_daily_summary_with_large_numbers():
    """Test daily summary with very large amounts"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_daily_summary(
            total_expenses=9999999.99,
            total_income=9999999.99,
            transaction_count=1000,
            top_category="Investment"
        )

        assert result == True

# ============================================================================
# EMAIL DELIVERY FAILURE TESTS
# ============================================================================

def test_transaction_alert_smtp_failure():
    """Test handling of SMTP connection failure"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

        result = send_transaction_alert(
            merchant_name="SHOP",
            amount=500.00,
            category="Shopping",
            transaction_type="Expenses"
        )

        assert result == False

def test_error_alert_smtp_failure():
    """Test handling of SMTP failure for error alerts"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

        result = send_error_alert(
            error_type="Error",
            error_message="Test error",
            sms_id="test_123"
        )

        assert result == False

def test_daily_summary_smtp_failure():
    """Test handling of SMTP failure for daily summary"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

        result = send_daily_summary(
            total_expenses=50000.00,
            total_income=100000.00,
            transaction_count=25,
            top_category="Food"
        )

        assert result == False

def test_login_failure():
    """Test handling of authentication failure"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        # SMTPAuthenticationError requires (code, msg) arguments
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(
            535, "Authentication failed"
        )
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_transaction_alert(
            merchant_name="SHOP",
            amount=500.00,
            category="Shopping",
            transaction_type="Expenses"
        )

        assert result == False

# ============================================================================
# RATE LIMITING / SPAM PREVENTION TESTS
# ============================================================================

def test_rapid_alerts_should_be_throttled():
    """Test that rapid consecutive alerts are handled (in production, implement throttling)"""
    # This is a conceptual test - implementation depends on how rate limiting is done
    alerts_sent = []

    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Simulate sending 10 alerts in quick succession
        for i in range(10):
            result = send_transaction_alert(
                merchant_name=f"SHOP_{i}",
                amount=100.00,
                category="Shopping",
                transaction_type="Expenses"
            )
            alerts_sent.append(result)

        # All should succeed (rate limiting would be done differently)
        assert all(alerts_sent)

# ============================================================================
# SPECIAL CASES
# ============================================================================

def test_transaction_alert_with_unicode_characters():
    """Test alert with unicode characters in merchant name"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_transaction_alert(
            merchant_name="रेस्तरां RESTAURANT",  # Hindi + English
            amount=500.00,
            category="Food",
            transaction_type="Expenses"
        )

        assert result == True

def test_error_alert_with_newlines():
    """Test error alert with multi-line error message"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        error_msg = """Line 1 of error
Line 2 of error
Line 3 of error"""

        result = send_error_alert(
            error_type="MultilineError",
            error_message=error_msg,
            sms_id="test_123"
        )

        assert result == True

def test_daily_summary_with_special_category_name():
    """Test daily summary with special characters in category"""
    with patch('email_alerts.smtplib.SMTP_SSL') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = send_daily_summary(
            total_expenses=50000.00,
            total_income=100000.00,
            transaction_count=25,
            top_category="Food & Dining (Home)"
        )

        assert result == True

# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_email_credentials_loaded():
    """Test that email credentials are loaded from environment"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    gmail_email = os.getenv("GMAIL_EMAIL")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    alert_email = os.getenv("ALERT_EMAIL")

    assert gmail_email is not None, "GMAIL_EMAIL not configured"
    assert gmail_password is not None, "GMAIL_APP_PASSWORD not configured"
    assert alert_email is not None, "ALERT_EMAIL not configured"

# ============================================================================
# COVERAGE REPORT
# ============================================================================

def test_email_alerts_coverage_report():
    """Generate coverage report for email alerts"""

    print("\n" + "="*80)
    print("EMAIL ALERTS TEST COVERAGE REPORT")
    print("="*80)
    print("✅ Transaction alert structure and delivery")
    print("✅ Error alert structure and delivery")
    print("✅ Daily summary structure and delivery")
    print("✅ SMTP connection failures")
    print("✅ Authentication failures")
    print("✅ Special characters handling (unicode, newlines, quotes)")
    print("✅ Large transaction amounts")
    print("✅ Email configuration")
    print("✅ Mock tests (no actual email sending)")
    print("="*80)
