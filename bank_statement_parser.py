"""
Axis Bank Statement PDF Parser
Extracts transactions from Axis Bank PDF statements
"""
import pdfplumber
import re
from datetime import datetime
from typing import List, Dict
from logger import log


def parse_bank_statement(pdf_path: str) -> List[Dict]:
    """
    Parse Axis Bank PDF statement and extract all transactions

    Returns list of transactions with:
    - date (DD-MM-YY)
    - amount (float)
    - type (debit/credit)
    - merchant_name (str)
    - description (str)
    """
    transactions = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"

            # Split by date patterns to find transaction lines
            # Pattern: DD-MM-YYYY at start of line
            lines = full_text.split("\n")

            for i, line in enumerate(lines):
                transaction = _parse_transaction_line(line, lines, i)
                if transaction:
                    transactions.append(transaction)

        log.info(f"[Bank Parser] Extracted {len(transactions)} transactions from PDF")
        return transactions

    except Exception as e:
        log.error(f"[Bank Parser] Error parsing PDF: {e}")
        return []


def _parse_transaction_line(line: str, all_lines: List[str], line_idx: int) -> Dict or None:
    """
    Parse a single transaction line from bank statement text

    Format: DD-MM-YYYY Transaction Details ... Amount Balance
    """
    try:
        line = line.strip()
        if not line:
            return None

        # Check if line starts with date pattern
        date_match = re.match(r'^(\d{2}-\d{2}-\d{4})\s+(.+)', line)
        if not date_match:
            return None

        date_str = date_match.group(1)
        rest = date_match.group(2)

        # Parse date
        try:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            date_formatted = date_obj.strftime("%d-%m-%y")
        except:
            return None

        # Extract amounts (last 2 numbers in line)
        # Format: ... Withdrawal Deposits Balance
        amounts = re.findall(r'[\d,]+\.?\d*', rest)
        if len(amounts) < 2:
            return None

        amount_str = amounts[-2]  # Second last is the transaction amount
        amount = float(amount_str.replace(",", ""))

        # Determine type based on position in line
        # Simple heuristic: if amount appears before "opening/closing", it's likely a transaction
        if amount == 0:
            return None

        # Extract description/merchant (everything between date and amounts)
        description = re.sub(r'[\d,]+\.?\d*\s+[\d,]+\.?\d*\s*$', '', rest).strip()
        merchant = _extract_merchant(description)

        # Guess type (debit/credit) based on common patterns
        tx_type = "debit"
        if any(keyword in description.upper() for keyword in ["CREDIT", "DEPOSITED", "CREDITED", "SALARY", "NEFT-CR"]):
            tx_type = "credit"

        return {
            "date": date_formatted,
            "amount": amount,
            "type": tx_type,
            "merchant_name": merchant,
            "description": description,
            "source": "bank_statement"
        }

    except Exception as e:
        return None


def _extract_merchant(details: str) -> str:
    """
    Extract merchant name from transaction details

    Examples:
    - "UPI/P2M/6491148674204/ZOMATO LIMITED /UPI/AXIS BANK" → "ZOMATO LIMITED"
    - "ACH-DR-GROWW PAY SERVICES P-00005J4CASFKTPQLSG261" → "GROWW PAY SERVICES"
    - "OUTWARD REM NO. 0741RI26159067 USD 204.02" → "OUTWARD REMITTANCE"
    """
    details = details.upper()

    # UPI pattern: extract between slashes
    upi_match = re.search(r'/([A-Z0-9\s]+)/UPI', details)
    if upi_match:
        return upi_match.group(1).strip()

    # ACH pattern: extract after ACH-xx-
    ach_match = re.search(r'ACH-[A-Z]{2}-([A-Z0-9\s]+?)(?:-|$)', details)
    if ach_match:
        return ach_match.group(1).strip()

    # Purchase pattern
    purchase_match = re.search(r'PURCHASE AT\s+([A-Z0-9\s]+)', details)
    if purchase_match:
        return purchase_match.group(1).strip()

    # Outward remittance
    if "OUTWARD REM" in details:
        return "OUTWARD REMITTANCE"

    # NEFT/IMPS pattern
    if "NEFT" in details or "IMPS" in details:
        match = re.search(r'(NEFT|IMPS)[^\n]*', details)
        if match:
            return match.group(0).strip()

    # Default: first 50 chars
    return details[:50].strip()


def compare_transactions(bank_txns: List[Dict], supabase_txns: List[Dict]) -> Dict:
    """
    Compare bank transactions with Supabase transactions

    Returns:
    {
        "missing": [],  # In bank but not in Supabase
        "matched": [],  # Found in both
        "unmatched": [] # In Supabase but not in bank
    }
    """
    missing = []
    matched = []

    # Create search index for Supabase transactions
    supabase_index = {}
    for txn in supabase_txns:
        key = f"{txn.get('amount')}_{txn.get('timestamp', '').split()[0]}"
        if key not in supabase_index:
            supabase_index[key] = []
        supabase_index[key].append(txn)

    # Check each bank transaction
    for bank_txn in bank_txns:
        key = f"{bank_txn['amount']}_{bank_txn['date']}"

        if key in supabase_index and supabase_index[key]:
            matched.append(bank_txn)
            supabase_index[key].pop(0)  # Mark as matched
        else:
            missing.append(bank_txn)

    return {
        "missing": missing,
        "matched": matched,
        "total_bank": len(bank_txns),
        "total_supabase": len(supabase_txns),
        "matched_count": len(matched)
    }
