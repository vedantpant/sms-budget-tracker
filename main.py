from parser import parse_sms, process_sms

from openpyxl_basic import add_to_excel

sms = """INR 1754.00 debited
A/c no. XX0316
22-04-26, 20:48:22
UPI/P2M/908328661126/SUKU JAPANESE AND T
Not you? SMS BLOCKUPI Cust ID to 919951860002"""

sms_new = """INR 320.00 debited
A/c no. XX0316
25-04-26, 14:30:00
UPI/P2M/123456789012/DOMINOS PIZZA HSR
Not you? SMS BLOCKUPI Cust ID to 919951860002"""

sms_test1 = """INR 250.00 debited
A/c no. XX0316
25-04-26, 14:30:00
UPI/P2M/123456789012/BURGER KING HSR
Not you? SMS BLOCKUPI Cust ID to 919951860002"""

sms_test2 = """INR 800.00 debited
A/c no. XX0316
25-04-26, 15:00:00
UPI/P2M/987654321012/DECATHLON SPORTS
Not you? SMS BLOCKUPI Cust ID to 919951860002"""

print(process_sms(sms_test1))
print(process_sms(sms_test2))

transaction = process_sms(sms_new)
print("parsed transaction:", transaction)

if transaction:
    add_to_excel(transaction)