from datetime import datetime
import re
import json
from difflib import get_close_matches
from ai_categorizer import categorize_merchant

sms1 = """INR 645.00 debited
A/c no. XX0316
20-04-26, 18:24:43
UPI/P2M/502760971106/CALIFORNIA BURRITO
Not you? SMS BLOCKUPI Cust ID to 919951860002"""

sms2 = """INR 1754.00 debited
A/c no. XX0316
22-04-26, 20:48:22
UPI/P2M/908328661126/SUKU JAPANESE AND T
Not you? SMS BLOCKUPI Cust ID to 919951860002"""

sms3 = """Debit INR 19904.58
Axis Bank A/c XX0316
20-04-26 10:05:31
OUTWARD REM NO. 0741RI2611
Not You? SMS BLOCKALL CustID to 919951860002"""

CATEGORIES = {
    "Expenses": [
        "Housing", "Utilities", "Groceries", "Transportation",
        "Insurances", "Clothing", "Body Care & Medicine", "Media",
        "Subscription", "Cook Salary", "Food Outside", 
        "Cleaner Salary", "Play Outside", "Fun & Vacation"
    ],
    "Income": [
        "Employment(Net)", "Side Hustle(Net)", "Money Return", "Dividends"
    ],
    "Savings": [
        "Emergency Fund", "Retirement Account", "Mutual Fund", "Stock Portfolio"
    ]
}

def get_category(merchant, amount=0):
    result = MERCHANT_CATEGORY_MAP.get(merchant, None)
    if result:
         return result
    
    merchants = list(MERCHANT_CATEGORY_MAP.keys())
    close = get_close_matches(merchant, merchants, n=1, cutoff=0.75)

    if close:
        print(f"Fuzzy match: '{merchant}' -> '{close[0]}'")
        return MERCHANT_CATEGORY_MAP[close[0]]
    
    result = handle_unknown_merchant(merchant, amount)
    if result:
        MERCHANT_CATEGORY_MAP[merchant] = result
        return result
    return MERCHANT_CATEGORY_MAP.get(merchant, None)
         

def parse_sms(sms):
    match = re.search(r'INR\s+(\d+\.\d{2})\s+debited\s+A/c\s+no\.\s+XX(\d+)\s+(\d{2}-\d{2}-\d{2}, \d{2}:\d{2}:\d{2})\s+UPI/P2[MA]/(\d+)/(.+)', sms)

    if match:
        return {
            "amount": match.group(1),
            "account_number": match.group(2),
            "timestamp": match.group(3),
            "transaction_id": match.group(4),
            "merchant_name": match.group(5)
        }
    
    match = re.search(r'Debit\sINR\s+(\d+\.\d{2})\s+Axis\s+Bank\s+A/c\s+XX(\d+)\s+(\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(OUTWARD\s+REM\s+NO\.\s+\w+)', sms)
    if match:
        return {
            "amount": match.group(1),
            "account_number": match.group(2),
            "timestamp": f"{match.group(3)}, {match.group(4)}",
            "transaction_id": "",
            "merchant_name": "OUTWARD REM"
        }
    
    # UPI Credit — "by Sender VPA xyz@upi on DD-MM-YY at HH:MM:SS"
    match = re.search(
        r'INR\s+([\d,]+\.?\d*)\s+credited\s+to\s+A/c\s+no\.\s+XX(\d+)\s+by\s+(.+?)\s+VPA\s+\S+\s+on\s+(\d{2}-\d{2}-\d{2})\s+at\s+(\d{2}:\d{2}:\d{2})',
        sms)
    if match:
        return {
            "amount": match.group(1).replace(",", ""),
            "account_number": match.group(2),
            "merchant_name": match.group(3).strip(),
            "timestamp": f"{match.group(4)}, {match.group(5)}",
            "transaction_id": "",
        }

    # ACH/Salary Credit — "at DD-MM-YY at HH:MM:SS by ACH-CR-..."
    match = re.search(
        r'INR\s+([\d,]+\.?\d*)\s+credited\s+to\s+A/c\s+no\.\s+XX(\d+)\s+(?:on\s+)?(?:at\s+)?(\d{2}-\d{2}-\d{2})\s+at\s+(\d{2}:\d{2}:\d{2})\s+by\s+(ACH-CR-\S+)',
        sms)
    if match:
        return {
            "amount": match.group(1).replace(",", ""),
            "account_number": match.group(2),
            "timestamp": f"{match.group(3)}, {match.group(4)}",
            "transaction_id": "",
            "merchant_name": match.group(5).strip(),
        }

    # Generic Credit fallback — no merchant extractable
    match = re.search(
    r'INR\s+([\d,]+\.?\d*)\s+credited\s+to\s+A/c\s+no\.\s+XX(\d+)\s+(?:on\s+)?(?:at\s+)?(\d{2}-\d{2}-\d{2}),?\s+(?:at\s+)?(\d{2}:\d{2}:\d{2})',
    sms)

    if match:
        return {
            "amount": match.group(1).replace(",", ""),
            "account_number": match.group(2),
            "timestamp": f"{match.group(3)}, {match.group(4)}",
            "transaction_id": "",
            "merchant_name": "CREDIT-UNKNOWN",
        }
    
    match = re.search(r'Debit\s+INR\s+([\d,]+\.?\d*)\s+Axis\s+Bank\s+A/c\s+XX(\d+)\s+(\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+ACH-DR-(.+?)[\n\r]',sms)
    if match:
        return {
            "amount": match.group(1).replace(",", ""),
            "account_number": match.group(2),
            "timestamp": f"{match.group(3)}, {match.group(4)}",
            "transaction_id": "",
            "merchant_name": "ACH-DR-Groww Pay Services"
        }
    
    match = re.search(
    r'NACH debit towards (.+?) for INR ([\d,]+\.?\d*)\s+with UMRN',
    sms)

    if match:
        merchant = match.group(1).strip()
        amount = match.group(2).replace(",", "")
        timestamp = datetime.now().strftime("%d-%m-%y, 00:00:00")
        return {
            "amount": amount,
            "account_number": "0316",
            "timestamp": timestamp,
            "transaction_id": "",
            "merchant_name": merchant
        }
    
    # Google Play auto debit
    match = re.search(
        r'INR\s+([\d,]+\.?\d*)\s+for\s+(.+?)\s+will be auto debited',
        sms
    )
    if match:
        amount = match.group(1).replace(",", "")
        merchant = match.group(2).strip()
        timestamp = datetime.now().strftime("%d-%m-%y, 00:00:00")
        return {
            "amount": amount,
            "account_number": "0316",
            "timestamp": timestamp,
            "transaction_id": "",
            "merchant_name": merchant
        }

    # Auto Pay processed
    match = re.search(
        r'Auto Pay of INR\s+([\d,]+\.?\d*)\s+for\s+(.+?)\s+has been processed',
        sms
    )
    if match:
        amount = match.group(1).replace(",", "")
        merchant = match.group(2).strip()
        timestamp = datetime.now().strftime("%d-%m-%y, 00:00:00")
        return {
            "amount": amount,
            "account_number": "0316",
            "timestamp": timestamp,
            "transaction_id": "",
            "merchant_name": merchant
        }

    return None

def process_sms(sms):
    parsed = parse_sms(sms)
    if parsed is None:
        print("Failed to parse SMS")
        return None
    
    category_info = get_category(parsed["merchant_name"], float(parsed["amount"]))

    return {
        "amount": parsed["amount"],
        "account_number": parsed["account_number"],
        "timestamp": parsed["timestamp"],
        "transaction_id": parsed["transaction_id"],
        "merchant_name": parsed["merchant_name"],
        "type": category_info["type"],
        "category": category_info["category"]
    }



with open("CATEGORY_MAP.json", "r") as f:
        MERCHANT_CATEGORY_MAP = json.load(f)


def handle_unknown_merchant(merchant_name, amt=0):

    result = categorize_merchant(merchant_name, amount=amt)
    if result:
        return result
    
    
    print(f"Unknown merchant: {merchant_name}. Please categorize this merchant.")

    types = list(CATEGORIES.keys())
    for i, t in enumerate(types, 1):
        print(f"{i}. {t}")
    try:    
        choice1 = int(input("Select type (1-3): "))
    except ValueError:
        print("Invalid input - skipping merchant")
        return
    type = types[choice1 - 1]

    categories = CATEGORIES[type]
    for i, c in enumerate(categories, 1):
        print(f"{i}. {c}")

    choice2 = int(input("Select category (1-10): "))
    category = categories[choice2 - 1]

    MERCHANT_CATEGORY_MAP[merchant_name] = {"type": type, "category": category}
    print(f"merchant {merchant_name} categorized as {type} - {category}")

    with open("CATEGORY_MAP.json", "w") as f:
        json.dump(MERCHANT_CATEGORY_MAP, f, indent=4)

    

# print(parse_sms(sms1))
# print(parse_sms(sms2))
# print("\n")
# print(get_category("rental payment"))

# handle_unknown_merchant("SWIGGY")
# print(get_category("CALIFORNIA BURRITO"))
# print(get_category("SWIGGY"))
# print(get_category("SWIGGY"))

# print(process_sms(sms1))
# print(process_sms(sms2))
# print(get_category("CALIFORNIA BURRITO "))  # extra space — fuzzy match hona chahiye
# print(get_category("SUKU JAPANESE"))         # short form — fuzzy match
# print(get_category("ZOMATO"))                # bilkul naya — user se poochha jaayega

# print(parse_sms(sms3))

# print(process_sms(sms3))