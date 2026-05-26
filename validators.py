# validator.py — Input validation & sanitization

import re
from exceptions import InvalidAmountError, MissingFieldError
from logger import log


def sanitize_sms(sms_body):
    """Clean and validate raw SMS text."""
    if not sms_body or not isinstance(sms_body, str):
        raise MissingFieldError("sms_body")

    # Remove null bytes and control characters
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', sms_body)

    # Trim whitespace
    cleaned = cleaned.strip()

    # Max length check (SMS shouldn't be > 1000 chars)
    if len(cleaned) > 1000:
        log.warning(f"SMS too long ({len(cleaned)} chars), truncating")
        cleaned = cleaned[:1000]

    if len(cleaned) < 10:
        raise MissingFieldError("sms_body (too short)")

    return cleaned


def validate_amount(amount_str):
    """Validate and parse amount from SMS."""
    try:
        cleaned = str(amount_str).replace(",", "").strip()
        amount = float(cleaned)
        if amount <= 0:
            raise InvalidAmountError(f"Amount must be positive: {amount}")
        if amount > 10_000_000:
            raise InvalidAmountError(f"Amount too large: {amount}")
        return amount
    except (ValueError, TypeError):
        raise InvalidAmountError(f"Cannot parse amount: {amount_str}")


def validate_merchant(merchant_name):
    """Validate and clean merchant name."""
    if not merchant_name or not isinstance(merchant_name, str):
        raise MissingFieldError("merchant_name")

    cleaned = merchant_name.strip()

    # Remove SQL injection attempts
    cleaned = re.sub(r'[;\'"\\]', '', cleaned)

    if len(cleaned) < 1:
        raise MissingFieldError("merchant_name (empty after cleaning)")

    return cleaned[:100]  # Max 100 chars


def validate_category(type_name, category_name):
    """Validate type and category values."""
    valid_types = {"Expenses", "Income", "Savings"}
    if type_name not in valid_types:
        raise ValueError(f"Invalid type: {type_name}. Must be one of {valid_types}")

    return type_name, category_name