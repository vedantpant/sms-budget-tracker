from parser import parse_sms, process_sms

from openpyxl_basic import add_to_excel

sms = """INR 1754.00 debited
A/c no. XX0316
22-04-26, 20:48:22
UPI/P2M/908328661126/SUKU JAPANESE AND T
Not you? SMS BLOCKUPI Cust ID to 919951860002"""

transaction = process_sms(sms)
print("parsed transaction:", transaction)

if transaction:
    add_to_excel(transaction)