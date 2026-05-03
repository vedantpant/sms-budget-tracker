# SMS Budget Tracker

Automated budget tracker that parses Axis Bank SMS transactions and updates Excel.

## Features
- Parses UPI, NEFT, Salary, Mutual Fund SMS formats
- Auto-categorizes merchants
- Duplicate detection using Transaction ID
- Bulk import from Termux SMS export

## Stack
- Python, win32com, openpyxl, difflib

## Usage
1. Export SMS from Termux
2. Run \python bulk_import.py\
3. Excel auto-updates with new transactions
