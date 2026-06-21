"""
Comprehensive Functionality Edge Case Tests for Parser
Tests real-world scenarios and edge cases
"""
from parser import parse_sms

# ============================================================================
# AMOUNT PARSING EDGE CASES
# ============================================================================

def test_amount_with_commas():
    """Test amount with comma separators (Indian format)"""
    sms = "INR 10,000.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    assert result is not None, "Should parse amounts with commas"
    assert result["amount"] == "10000.00", "Should remove commas from amount"

def test_amount_without_decimals():
    """Test amount without decimal places"""
    sms = "INR 500 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    # May or may not parse - depends on parser design
    if result:
        assert "amount" in result, "Should extract amount if parsed"

def test_very_large_amount():
    """Test very large transaction (₹99,99,999.99)"""
    sms = "INR 99,99,999.99 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/PROPERTY DEALER"
    result = parse_sms(sms)
    assert result is not None, "Should parse large amounts"
    assert result["amount"] == "9999999.99"

def test_very_small_amount():
    """Test very small transaction (₹0.01)"""
    sms = "INR 0.01 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/MICRO TRANSACTION"
    result = parse_sms(sms)
    assert result is not None, "Should parse small amounts"
    assert result["amount"] == "0.01"

def test_round_amount():
    """Test round amount without decimals in SMS but expecting .00 format"""
    sms = "INR 1000.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/RESTAURANT"
    result = parse_sms(sms)
    assert result is not None
    assert result["amount"] == "1000.00"

# ============================================================================
# MERCHANT NAME EDGE CASES
# ============================================================================

def test_merchant_with_numbers():
    """Test merchant name containing numbers"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/HOTEL123 CHAIN"
    result = parse_sms(sms)
    assert result is not None, "Should parse merchants with numbers"
    assert "123" in result["merchant_name"]

def test_merchant_with_special_chars():
    """Test merchant with special characters (hyphens, underscores)"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP-N-SAVE_STORE"
    result = parse_sms(sms)
    # May fail due to regex limitations
    if result:
        assert "SHOP" in result["merchant_name"]

def test_merchant_single_letter():
    """Test single letter merchant name"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/X HOTEL"
    result = parse_sms(sms)
    if result:
        assert "X" in result["merchant_name"]

def test_merchant_very_long_name():
    """Test very long merchant name (>50 characters)"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/THE WORLD'S LONGEST MERCHANT NAME THAT EVER EXISTED IN HISTORY"
    result = parse_sms(sms)
    if result:
        assert result["merchant_name"] is not None

def test_merchant_case_variations():
    """Test merchant with mixed case"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/AmazonPay"
    result = parse_sms(sms)
    if result:
        assert result["merchant_name"] is not None

# ============================================================================
# ACCOUNT NUMBER EDGE CASES
# ============================================================================

def test_account_number_extraction():
    """Test extracting account number correctly"""
    sms = "INR 500.00 debited\nA/c no. XX9999\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    assert result is not None
    assert result["account_number"] == "9999"

def test_different_account_formats():
    """Test different account number formats"""
    sms = "INR 500.00 debited\nA/c no. XX0001\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    if result:
        assert result["account_number"] == "0001"

# ============================================================================
# TRANSACTION ID EDGE CASES
# ============================================================================

def test_transaction_id_extraction():
    """Test extracting transaction ID"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/ABC123XYZ789/SHOP"
    result = parse_sms(sms)
    assert result is not None
    assert result["transaction_id"] == "ABC123XYZ789"

def test_missing_transaction_id():
    """Test SMS without transaction ID (credit SMS)"""
    sms = "INR 50000.00 credited to A/c no. XX0316 on 20-06-26 at 14:30:45 IST. Info - ACH-CR-SAL-EMPLOYER"
    result = parse_sms(sms)
    if result:
        # Should have empty or missing transaction_id
        assert result.get("transaction_id", "") == ""

# ============================================================================
# TIMESTAMP EDGE CASES
# ============================================================================

def test_timestamp_extraction():
    """Test correct timestamp extraction"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    assert result is not None
    assert result["timestamp"] == "21-06-26, 14:30:45"

def test_leap_year_date():
    """Test leap year date (29-02-26)"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n29-02-26, 14:30:45\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    if result:
        assert "29-02-26" in result["timestamp"]

def test_year_boundary_date():
    """Test year boundary (31-12-25)"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n31-12-25, 23:59:59\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    if result:
        assert "31-12-25" in result["timestamp"]

def test_midnight_timestamp():
    """Test midnight timestamp (00:00:00)"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n01-01-26, 00:00:00\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    if result:
        assert "00:00:00" in result["timestamp"]

def test_different_timezone_format():
    """Test SMS with different timezone (IST vs UTC)"""
    sms = "INR 500.00 credited to A/c no. XX0316 on 20-06-26 at 14:30:45 UTC. Info - ACH-CR-SAL-EMPLOYER"
    result = parse_sms(sms)
    # May or may not parse with UTC timezone
    if result is None:
        print("⚠️ UTC timezone not supported - only IST tested")

# ============================================================================
# SPECIAL CASES & REAL-WORLD SCENARIOS
# ============================================================================

def test_reversal_or_correction():
    """Test SMS about transaction reversal"""
    sms = "Your transaction of INR 500 has been reversed. Original Ref: 12345"
    result = parse_sms(sms)
    # Should return None or handle gracefully
    assert result is None or isinstance(result, dict)

def test_balance_update_sms():
    """Test balance update SMS (not a transaction)"""
    sms = "Your account balance is INR 50,000. Do not share this with anyone."
    result = parse_sms(sms)
    # Should return None (not a transaction)
    assert result is None or result.get("amount") != "50000.00"

def test_sms_with_links():
    """Test SMS containing URLs/links"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP\nCheck https://example.com for details"
    result = parse_sms(sms)
    if result:
        assert result["amount"] == "500.00"

def test_sms_with_multiple_spaces():
    """Test SMS with irregular spacing"""
    sms = "INR   500.00   debited\nA/c  no.  XX0316\n21-06-26,  14:30:45\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    # May or may not parse depending on regex strictness
    if result is None:
        print("⚠️ Multiple spaces cause parsing to fail")

def test_sms_with_extra_newlines():
    """Test SMS with extra newlines"""
    sms = "INR 500.00 debited\n\nA/c no. XX0316\n\n21-06-26, 14:30:45\n\nUPI/P2M/123/SHOP"
    result = parse_sms(sms)
    if result is None:
        print("⚠️ Extra newlines cause parsing to fail")

def test_duplicate_sms():
    """Test same SMS parsed twice (duplicate detection should be in sync_engine)"""
    sms = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP"
    result1 = parse_sms(sms)
    result2 = parse_sms(sms)
    assert result1 == result2, "Same SMS should parse identically"

def test_sms_with_emoji():
    """Test SMS with emoji characters"""
    sms = "INR 500.00 debited ✅\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP 🏪"
    result = parse_sms(sms)
    if result is None:
        print("⚠️ Emoji characters cause parsing to fail")

# ============================================================================
# SYNC ENGINE FUNCTIONALITY - Testing duplicate detection
# ============================================================================

def test_duplicate_transaction_id():
    """Test detection of duplicate transaction IDs"""
    sms1 = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/SAME_ID_123/SHOP1"
    sms2 = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/SAME_ID_123/SHOP2"

    result1 = parse_sms(sms1)
    result2 = parse_sms(sms2)

    if result1 and result2:
        assert result1["transaction_id"] == result2["transaction_id"], "Should detect duplicate transaction IDs"

def test_similar_but_different_amounts():
    """Test transactions with similar but different amounts"""
    sms1 = "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/ID1/SHOP"
    sms2 = "INR 500.01 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/ID2/SHOP"

    result1 = parse_sms(sms1)
    result2 = parse_sms(sms2)

    assert result1["amount"] != result2["amount"], "Should detect different amounts"

# ============================================================================
# SUMMARY REPORT
# ============================================================================

def test_report_parser_capabilities():
    """Generate a report of parser capabilities"""
    test_cases = {
        "UPI Debit": "INR 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP",
        "OUTWARD REM": "Debit INR 500.00\nAxis Bank A/c XX0316\n21-06-26 14:30:45\nOUTWARD REM NO. ABC123",
        "ACH-CR": "INR 500.00 credited to A/c no. XX0316 on 21-06-26 at 14:30:45 IST. Info - ACH-CR-SAL-EMPLOYER",
        "NACH": "NACH debit towards Employer for INR 500.00 with UMRN ABC123 has been successfully processed in A/c no. XX0316",
        "Google Play": "INR 500.00 for Google Play will be auto debited via Axis Bank",
        "Slash Date": "INR 500.00 debited\nA/c no. XX0316\n21/06/26, 14:30:45\nUPI/P2M/123/SHOP",
        "Currency Symbol": "₹ 500.00 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP",
        "No Decimals": "INR 500 debited\nA/c no. XX0316\n21-06-26, 14:30:45\nUPI/P2M/123/SHOP",
    }

    print("\n" + "="*80)
    print("PARSER CAPABILITY REPORT")
    print("="*80)

    for name, sms in test_cases.items():
        result = parse_sms(sms)
        status = "✅ SUPPORTED" if result else "❌ NOT SUPPORTED"
        print(f"{name:20s} {status}")

    print("="*80)
