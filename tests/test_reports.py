"""
Comprehensive tests for Report Generator and Email Alerts
Tests daily, weekly, and monthly expenditure reports
"""
from report_generator import ReportGenerator
from email_alerts import send_daily_report, send_weekly_report, send_monthly_report
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytest

# ============================================================================
# REPORT GENERATOR TESTS
# ============================================================================

def test_report_generator_initialization():
    """Test ReportGenerator initializes correctly"""
    generator = ReportGenerator()
    assert generator is not None
    assert hasattr(generator, 'db')

@patch('report_generator.SupabaseClient')
def test_get_daily_transactions(mock_db_class):
    """Test getting daily transactions"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 500, "merchant_name": "SHOP", "type": "Expenses", "category": "Food"},
        {"amount": 100, "merchant_name": "CAFE", "type": "Expenses", "category": "Food"}
    ]
    mock_db_class.return_value = mock_db

    generator = ReportGenerator()
    transactions = generator.get_daily_transactions()

    assert transactions is not None
    assert len(transactions) == 2

@patch('report_generator.SupabaseClient')
def test_get_weekly_transactions(mock_db_class):
    """Test getting weekly transactions"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 500, "merchant_name": "SHOP", "type": "Expenses", "category": "Food"},
        {"amount": 200, "merchant_name": "GAS", "type": "Expenses", "category": "Transport"},
        {"amount": 1000, "merchant_name": "SALARY", "type": "Income", "category": "Income"}
    ]
    mock_db_class.return_value = mock_db

    generator = ReportGenerator()
    transactions = generator.get_weekly_transactions()

    assert transactions is not None
    assert len(transactions) == 3

@patch('report_generator.SupabaseClient')
def test_get_monthly_transactions(mock_db_class):
    """Test getting monthly transactions"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 5000, "merchant_name": "RENT", "type": "Expenses", "category": "Housing"},
        {"amount": 2000, "merchant_name": "SALARY", "type": "Income", "category": "Income"}
    ]
    mock_db_class.return_value = mock_db

    generator = ReportGenerator()
    transactions = generator.get_monthly_transactions()

    assert transactions is not None
    assert len(transactions) == 2

# ============================================================================
# CALCULATION TESTS
# ============================================================================

@patch('report_generator.SupabaseClient')
def test_calculate_totals_by_category(mock_db_class):
    """Test calculating totals by category"""
    mock_db_class.return_value = MagicMock()

    transactions = [
        {"amount": 500, "type": "Expenses", "category": "Food"},
        {"amount": 300, "type": "Expenses", "category": "Food"},
        {"amount": 200, "type": "Expenses", "category": "Transport"},
        {"amount": 1000, "type": "Income", "category": "Income"}  # Should be ignored
    ]

    generator = ReportGenerator()
    result = generator.calculate_totals_by_category(transactions)

    assert result["Food"]["amount"] == 800
    assert result["Food"]["count"] == 2
    assert result["Transport"]["amount"] == 200
    assert result["Transport"]["count"] == 1
    assert "Income" not in result  # Income should not be included

@patch('report_generator.SupabaseClient')
def test_get_top_merchants(mock_db_class):
    """Test getting top merchants by spending"""
    mock_db_class.return_value = MagicMock()

    transactions = [
        {"amount": 500, "type": "Expenses", "merchant_name": "SHOP A"},
        {"amount": 800, "type": "Expenses", "merchant_name": "SHOP B"},
        {"amount": 200, "type": "Expenses", "merchant_name": "SHOP C"},
        {"amount": 1000, "type": "Expenses", "merchant_name": "SHOP D"},
        {"amount": 100, "type": "Expenses", "merchant_name": "SHOP E"},
        {"amount": 150, "type": "Expenses", "merchant_name": "SHOP F"},
    ]

    generator = ReportGenerator()
    top_merchants = generator.get_top_merchants(transactions, limit=3)

    assert len(top_merchants) == 3
    assert top_merchants[0][0] == "SHOP D"  # 1000
    assert top_merchants[1][0] == "SHOP B"  # 800
    assert top_merchants[2][0] == "SHOP A"  # 500

@patch('report_generator.SupabaseClient')
def test_calculate_total_spending(mock_db_class):
    """Test calculating total spending"""
    mock_db_class.return_value = MagicMock()

    transactions = [
        {"amount": 500, "type": "Expenses"},
        {"amount": 300, "type": "Expenses"},
        {"amount": 1000, "type": "Income"}  # Should be ignored
    ]

    generator = ReportGenerator()
    total = generator.calculate_total_spending(transactions)

    assert total == 800

@patch('report_generator.SupabaseClient')
def test_calculate_total_income(mock_db_class):
    """Test calculating total income"""
    mock_db_class.return_value = MagicMock()

    transactions = [
        {"amount": 500, "type": "Expenses"},
        {"amount": 50000, "type": "Income"},
        {"amount": 10000, "type": "Income"}
    ]

    generator = ReportGenerator()
    total = generator.calculate_total_income(transactions)

    assert total == 60000

# ============================================================================
# REPORT FORMAT TESTS
# ============================================================================

@patch('report_generator.SupabaseClient')
def test_format_daily_report_with_transactions(mock_db_class):
    """Test formatting daily report with transactions"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 500, "merchant_name": "SHOP", "type": "Expenses", "category": "Shopping"},
        {"amount": 200, "merchant_name": "CAFE", "type": "Expenses", "category": "Food"}
    ]
    mock_db_class.return_value = mock_db

    generator = ReportGenerator()
    report = generator.format_daily_report()

    assert report is not None
    assert "subject" in report
    assert "html_body" in report
    assert report["total_spent"] == 700
    assert report["transaction_count"] == 2
    assert "SHOP" in str(report["top_merchants"])

@patch('report_generator.SupabaseClient')
def test_format_daily_report_no_transactions(mock_db_class):
    """Test formatting daily report with no transactions"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = []
    mock_db_class.return_value = mock_db

    generator = ReportGenerator()
    report = generator.format_daily_report()

    assert report["total_spent"] == 0
    assert report["transaction_count"] == 0
    assert "No transactions" in report["html_body"]

@patch('report_generator.SupabaseClient')
def test_format_weekly_report(mock_db_class):
    """Test formatting weekly report"""
    mock_db = MagicMock()
    # Mock for current week
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 500, "merchant_name": "SHOP", "type": "Expenses", "category": "Shopping"},
        {"amount": 200, "merchant_name": "CAFE", "type": "Expenses", "category": "Food"}
    ]
    mock_db_class.return_value = mock_db

    generator = ReportGenerator()
    report = generator.format_weekly_report()

    assert report is not None
    assert "subject" in report
    assert "Weekly" in report["subject"]
    assert report["total_spent"] == 700

@patch('report_generator.SupabaseClient')
def test_format_monthly_report(mock_db_class):
    """Test formatting monthly report"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 5000, "merchant_name": "RENT", "type": "Expenses", "category": "Housing"},
        {"amount": 2000, "merchant_name": "GROCERIES", "type": "Expenses", "category": "Food"}
    ]
    mock_db_class.return_value = mock_db

    generator = ReportGenerator()
    report = generator.format_monthly_report()

    assert report is not None
    assert "subject" in report
    assert "Monthly" in report["subject"]
    assert report["total_spent"] == 7000

# ============================================================================
# EMAIL ALERT TESTS FOR REPORTS
# ============================================================================

@patch('email_alerts.smtplib.SMTP_SSL')
@patch('report_generator.SupabaseClient')
def test_send_daily_report(mock_db_class, mock_smtp):
    """Test sending daily report via email"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 500, "merchant_name": "SHOP", "type": "Expenses", "category": "Shopping"}
    ]
    mock_db_class.return_value = mock_db

    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    result = send_daily_report()

    assert result == True
    mock_server.sendmail.assert_called()

@patch('email_alerts.smtplib.SMTP_SSL')
@patch('report_generator.SupabaseClient')
def test_send_weekly_report(mock_db_class, mock_smtp):
    """Test sending weekly report via email"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 500, "merchant_name": "SHOP", "type": "Expenses", "category": "Shopping"}
    ]
    mock_db_class.return_value = mock_db

    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    result = send_weekly_report()

    assert result == True
    mock_server.sendmail.assert_called()

@patch('email_alerts.smtplib.SMTP_SSL')
@patch('report_generator.SupabaseClient')
def test_send_monthly_report(mock_db_class, mock_smtp):
    """Test sending monthly report via email"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 5000, "merchant_name": "RENT", "type": "Expenses", "category": "Housing"}
    ]
    mock_db_class.return_value = mock_db

    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    result = send_monthly_report()

    assert result == True
    mock_server.sendmail.assert_called()

@patch('email_alerts.smtplib.SMTP_SSL')
@patch('report_generator.SupabaseClient')
def test_send_report_smtp_failure(mock_db_class, mock_smtp):
    """Test handling SMTP failure for reports"""
    mock_db = MagicMock()
    mock_db_class.return_value = mock_db

    import smtplib
    mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

    result = send_daily_report()

    assert result == False

# ============================================================================
# HTML REPORT STRUCTURE TESTS
# ============================================================================

@patch('report_generator.SupabaseClient')
def test_html_report_contains_required_elements(mock_db_class):
    """Test that HTML report contains all required elements"""
    mock_db = MagicMock()
    mock_db.client.table.return_value.select.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"amount": 500, "merchant_name": "SHOP A", "type": "Expenses", "category": "Shopping"},
        {"amount": 300, "merchant_name": "SHOP B", "type": "Expenses", "category": "Food"}
    ]
    mock_db_class.return_value = mock_db

    generator = ReportGenerator()
    report = generator.format_daily_report()
    html = report["html_body"]

    # Check for required sections
    assert "DAILY SPENDING REPORT" in html or "daily" in html.lower()
    assert "TOTAL SPENDING" in html or "total" in html.lower()
    assert "TOP MERCHANTS" in html or "merchants" in html.lower()
    assert "CATEGORY" in html or "category" in html.lower()
    assert "₹" in html  # Currency symbol
    assert "800" in html or "800.00" in html  # Total amount (500 + 300)

# ============================================================================
# COVERAGE REPORT
# ============================================================================

def test_report_generator_coverage_report():
    """Generate coverage report for report system"""
    print("\n" + "="*80)
    print("REPORT GENERATOR TEST COVERAGE REPORT")
    print("="*80)
    print("✅ Report Generator Initialization")
    print("✅ Daily/Weekly/Monthly Transaction Queries")
    print("✅ Category Totals Calculation")
    print("✅ Top Merchants Extraction")
    print("✅ Total Spending & Income Calculation")
    print("✅ Report Formatting (HTML)")
    print("✅ Email Alert Sending")
    print("✅ SMTP Failure Handling")
    print("✅ HTML Structure Validation")
    print("✅ Empty Data Handling")
    print("="*80)
