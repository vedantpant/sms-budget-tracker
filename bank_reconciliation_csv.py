"""
Bank Statement Reconciliation (CSV Version)
Comprehensive reconciliation with duplicate avoidance and detailed reporting
"""
import pandas as pd
from supabase_client import SupabaseClient
from sync_engine import SyncEngine
from logger import log
from typing import List, Dict
from datetime import datetime


class CSVBankReconciliation:
    """Reconcile bank statements from CSV files with duplicate avoidance"""

    def __init__(self):
        self.supabase = SupabaseClient()
        self.sync_engine = SyncEngine()

    def reconcile_csv(self, csv_path: str, quick_mode: bool = False) -> Dict:
        """
        Comprehensive reconciliation workflow:
        1. Parse bank CSV
        2. Get Supabase transactions
        3. Check for duplicates (same date + amount)
        4. Find truly missing transactions
        5. Auto-add only new ones (skip AI if quick_mode=True)
        6. Return detailed report

        quick_mode: If True, skip AI categorization for known merchants (faster)
        """
        log.info(f"[Reconciliation] Starting reconciliation for {csv_path} (quick_mode={quick_mode})")

        try:
            # Step 1: Parse CSV
            bank_transactions = self._parse_csv_rows(csv_path)
            if not bank_transactions:
                return {"error": "No transactions in CSV"}

            log.info(f"[Reconciliation] Found {len(bank_transactions)} bank transactions")

            # Step 2: Get Supabase transactions
            supabase_txns = self.supabase.get_all_transactions()
            log.info(f"[Reconciliation] Found {len(supabase_txns)} Supabase transactions")

            # Step 3: Compare and categorize
            comparison = self._compare_transactions(bank_transactions, supabase_txns)

            log.info(f"[Reconciliation] Matched: {comparison['matched_count']}, "
                    f"Missing: {len(comparison['missing'])}")

            # Step 4: Auto-add missing (with duplicate check)
            added_count = 0
            if comparison['missing']:
                added_count = self._add_missing_transactions(
                    comparison['missing'],
                    supabase_txns,
                    quick_mode=quick_mode
                )

            # Step 5: Generate report
            report = self._generate_report(comparison, added_count)

            return {
                "status": "success",
                "total_bank_txns": len(bank_transactions),
                "total_supabase_txns": len(supabase_txns),
                "matched": comparison['matched_count'],
                "missing": len(comparison['missing']),
                "added": added_count,
                "failed": len(comparison['missing']) - added_count,
                "missing_details": comparison['missing'][:20],
                "matched_details": comparison['matched'][:10],
                "report": report
            }

        except Exception as e:
            log.error(f"[Reconciliation] Error: {e}")
            return {"error": str(e)}

    def _parse_csv_rows(self, csv_path: str) -> List[Dict]:
        """Parse CSV into transactions"""
        transactions = []

        try:
            df = pd.read_csv(csv_path)
            log.info(f"[CSV] Loaded {len(df)} rows")

            for idx, row in df.iterrows():
                try:
                    date_str = str(row.get('Date', '')).strip()
                    details = str(row.get('Transaction Details', '')).strip()
                    withdrawal = row.get('Withdrawal', None)
                    deposit = row.get('Deposits', None)

                    if not date_str or not details:
                        continue

                    # Parse date
                    try:
                        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                        date_formatted = date_obj.strftime("%d-%m-%y")
                    except:
                        continue

                    # Determine amount and type
                    amount = None
                    tx_type = None

                    if pd.notna(withdrawal) and withdrawal != "":
                        try:
                            amount = float(str(withdrawal).replace(",", ""))
                            tx_type = "debit"
                        except:
                            pass

                    if pd.notna(deposit) and deposit != "":
                        try:
                            amount = float(str(deposit).replace(",", ""))
                            tx_type = "credit"
                        except:
                            pass

                    if not amount or not tx_type:
                        continue

                    # Extract merchant
                    merchant = self._extract_merchant(details)

                    transactions.append({
                        "date": date_formatted,
                        "amount": amount,
                        "type": tx_type,
                        "merchant_name": merchant,
                        "description": details
                    })

                except Exception as e:
                    log.warning(f"[CSV] Error parsing row {idx}: {e}")
                    continue

            return transactions

        except Exception as e:
            log.error(f"[CSV] Error reading CSV: {e}")
            return []

    def _extract_merchant(self, details: str) -> str:
        """Extract merchant name from transaction details"""
        import re
        details = details.upper()

        # UPI pattern
        upi_match = re.search(r'/([A-Z0-9\s]+)/UPI', details)
        if upi_match:
            return upi_match.group(1).strip()

        # ACH pattern
        ach_match = re.search(r'ACH-[A-Z]{2}-([A-Z0-9\s]+?)(?:-|$)', details)
        if ach_match:
            return ach_match.group(1).strip()

        # NEFT/IMPS
        if "NEFT" in details:
            return "NEFT TRANSFER"
        if "IMPS" in details:
            return "IMPS TRANSFER"

        # Purchase pattern
        if "PURCHASE AT" in details:
            match = re.search(r'PURCHASE AT\s+([A-Z0-9\s]+)', details)
            if match:
                return match.group(1).strip()

        # Outward Remittance
        if "OUTWARD REM" in details:
            return "OUTWARD REMITTANCE"

        # Default
        return details[:50].strip()

    def _compare_transactions(self, bank_txns: List[Dict], supabase_txns: List[Dict]) -> Dict:
        """
        Compare bank and Supabase transactions
        Returns: matched, missing
        """
        missing = []
        matched = []

        # Create index for Supabase (amount + date as key)
        supabase_index = {}
        for txn in supabase_txns:
            # Extract date part (YYYY-MM-DD)
            txn_date = txn.get('timestamp', '').split()[0] if txn.get('timestamp') else ''
            # Convert to DD-MM-YY format for comparison
            if txn_date:
                parts = txn_date.split('-')
                if len(parts) == 3:
                    formatted_date = f"{parts[2][-2:]}-{parts[1]}-{parts[0][2:]}"
                    key = f"{txn['amount']}_{formatted_date}"
                    if key not in supabase_index:
                        supabase_index[key] = []
                    supabase_index[key].append(txn)

        # Check each bank transaction
        for bank_txn in bank_txns:
            key = f"{bank_txn['amount']}_{bank_txn['date']}"

            if key in supabase_index and supabase_index[key]:
                matched.append(bank_txn)
                supabase_index[key].pop(0)
            else:
                missing.append(bank_txn)

        return {
            "matched_count": len(matched),
            "matched": matched,
            "missing": missing,
            "total_bank": len(bank_txns)
        }

    def _add_missing_transactions(self, missing_txns: List[Dict],
                                 supabase_txns: List[Dict],
                                 quick_mode: bool = False) -> int:
        """
        Add missing transactions to Supabase ONLY
        Skip Excel to avoid any duplication issues

        quick_mode: If True, use only existing category mapping (skip AI)
        """
        added = 0

        for txn in missing_txns:
            try:
                amount = txn['amount']
                merchant = txn['merchant_name']
                date = txn['date']
                tx_type = txn['type']

                # Categorize
                if quick_mode:
                    # Quick mode: only use existing category map, skip Ollama AI
                    if merchant in self.sync_engine.category_map:
                        cat_info = self.sync_engine.category_map[merchant]
                        category = cat_info.get('category', 'Uncategorized')
                    else:
                        category = 'Uncategorized'
                else:
                    # Full mode: use AI categorization
                    category = self.sync_engine.categorize(
                        merchant=merchant,
                        amount=amount
                    )

                # Convert date
                date_obj = datetime.strptime(date, "%d-%m-%y")
                timestamp = date_obj.strftime("%Y-%m-%d 00:00:00")

                # Generate transaction ID
                import uuid
                transaction_id = f"BANK_{uuid.uuid4().hex[:12].upper()}"

                # Insert to Supabase ONLY
                result = self.supabase.insert_transaction({
                    'sms_id': None,
                    'amount': amount,
                    'merchant_name': merchant,
                    'type': tx_type,
                    'category': category,
                    'transaction_id': transaction_id,
                    'timestamp': timestamp,
                    'account_number': '0316'
                })

                if result:
                    added += 1
                    log.info(f"[Reconciliation] Added: {merchant} - INR {amount}")

            except Exception as e:
                log.error(f"[Reconciliation] Error: {e}")
                continue

        log.info(f"[Reconciliation] Added {added}/{len(missing_txns)} transactions to Supabase")
        return added

    def _generate_report(self, comparison: Dict, added: int) -> str:
        """Generate human-readable reconciliation report"""
        report = []
        report.append("=" * 90)
        report.append("BANK RECONCILIATION REPORT")
        report.append("=" * 90)
        report.append("")

        report.append("SUMMARY:")
        report.append(f"  Total Bank Transactions:     {comparison['total_bank']}")
        report.append(f"  Already in Supabase:         {comparison['matched_count']}")
        report.append(f"  Missing (Not in DB):         {len(comparison['missing'])}")
        report.append(f"  Successfully Added:          {added}")
        report.append(f"  Failed to Add:               {len(comparison['missing']) - added}")
        report.append("")

        if len(comparison['matched']) > 0:
            report.append("ALREADY IN SUPABASE (Duplicates Avoided):")
            report.append("-" * 90)
            for i, txn in enumerate(comparison['matched'][:10], 1):
                report.append(f"{i:2}. {txn['date']} | {txn['merchant_name']:<45} | {txn['amount']:>10.2f} ({txn['type']})")
            if len(comparison['matched']) > 10:
                report.append(f"    ... and {len(comparison['matched']) - 10} more already in DB")
            report.append("")

        if len(comparison['missing']) > 0:
            report.append("MISSING TRANSACTIONS (Not in Supabase - ADDED):")
            report.append("-" * 90)
            for i, txn in enumerate(comparison['missing'][:20], 1):
                report.append(f"{i:2}. {txn['date']} | {txn['merchant_name']:<45} | {txn['amount']:>10.2f} ({txn['type']})")
            if len(comparison['missing']) > 20:
                report.append(f"    ... and {len(comparison['missing']) - 20} more missing transactions")
            report.append("")

        report.append("=" * 90)
        report.append("NEXT STEPS:")
        report.append("  1. Check Supabase transactions table to verify new entries")
        report.append("  2. Review categorization accuracy")
        report.append("  3. Run your Excel reconciliation to sync")
        report.append("=" * 90)

        return "\n".join(report)
