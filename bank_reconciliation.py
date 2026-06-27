"""
Bank Statement Reconciliation
Compares bank statements with Supabase transactions and auto-syncs
"""
from bank_statement_parser import parse_bank_statement, compare_transactions
from supabase_client import SupabaseClient
from sync_engine import SyncEngine
from openpyxl_basic import add_bulk_to_excel
from logger import log
from typing import List, Dict
from datetime import datetime


class BankReconciliation:
    """Reconcile bank statements with Supabase transactions"""

    def __init__(self):
        self.supabase = SupabaseClient()
        self.sync_engine = SyncEngine()

    def reconcile_pdf(self, pdf_path: str) -> Dict:
        """
        Full reconciliation workflow:
        1. Parse bank PDF
        2. Get Supabase transactions
        3. Compare and find gaps
        4. Auto-add missing transactions
        """
        log.info(f"[Reconciliation] Starting reconciliation for {pdf_path}")

        # Step 1: Parse PDF
        bank_transactions = parse_bank_statement(pdf_path)
        if not bank_transactions:
            log.error("[Reconciliation] No transactions found in PDF")
            return {"error": "No transactions in PDF"}

        log.info(f"[Reconciliation] Found {len(bank_transactions)} bank transactions")

        # Step 2: Get Supabase transactions
        supabase_txns = self.supabase.get_all_transactions()
        log.info(f"[Reconciliation] Found {len(supabase_txns)} Supabase transactions")

        # Step 3: Compare
        comparison = compare_transactions(bank_transactions, supabase_txns)
        log.info(f"[Reconciliation] Matched: {comparison['matched_count']}, "
                f"Missing: {len(comparison['missing'])}")

        # Step 4: Auto-add missing
        added_count = 0
        if comparison['missing']:
            added_count = self._add_missing_transactions(comparison['missing'])

        return {
            "status": "success",
            "total_bank_txns": comparison['total_bank'],
            "total_supabase_txns": comparison['total_supabase'],
            "matched": comparison['matched_count'],
            "missing": len(comparison['missing']),
            "added": added_count,
            "missing_details": comparison['missing'][:10]  # First 10 for review
        }

    def _add_missing_transactions(self, missing_txns: List[Dict]) -> int:
        """
        Add missing transactions to Supabase and Excel

        Each transaction:
        1. Categorize using sync_engine
        2. Insert to Supabase
        3. Add to Excel
        """
        added = 0

        for txn in missing_txns:
            try:
                # Prepare transaction
                amount = txn['amount']
                merchant = txn['merchant_name']
                date = txn['date']
                tx_type = txn['type']

                # Categorize using existing logic
                category = self.sync_engine.categorize(
                    amount=amount,
                    merchant=merchant,
                    tx_type=tx_type
                )

                # Convert date format
                date_obj = datetime.strptime(date, "%d-%m-%y")
                timestamp = date_obj.strftime("%Y-%m-%d 00:00:00")

                # Insert to Supabase
                result = self.supabase.insert_transaction(
                    sms_id=None,  # No SMS for reconciled transactions
                    amount=amount,
                    merchant_name=merchant,
                    tx_type=tx_type,
                    category=category,
                    timestamp=timestamp
                )

                if result:
                    # Add to Excel
                    add_bulk_to_excel(
                        transactions=[{
                            "merchant": merchant,
                            "amount": amount,
                            "category": category,
                            "type": tx_type,
                            "date": date
                        }]
                    )
                    added += 1
                    log.info(f"[Reconciliation] Added: {merchant} - ₹{amount}")

            except Exception as e:
                log.error(f"[Reconciliation] Error adding transaction: {e}")
                continue

        log.info(f"[Reconciliation] Successfully added {added}/{len(missing_txns)} transactions")
        return added

    def get_reconciliation_status(self) -> Dict:
        """Get current reconciliation status"""
        try:
            supabase_count = len(self.supabase.get_all_transactions())
            return {
                "status": "healthy",
                "total_transactions": supabase_count,
                "last_sync": datetime.now().isoformat()
            }
        except Exception as e:
            log.error(f"[Reconciliation] Status check failed: {e}")
            return {"status": "error", "message": str(e)}
