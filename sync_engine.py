from logger import log
from supabase_client import SupabaseClient
from parser import parse_sms
from exceptions import SupabaseConnectionError
from difflib import get_close_matches
from ai_categorizer import ask_ollama
from datetime import datetime
from openpyxl_basic import add_to_excel
from config import Config
from datetime import datetime


class SyncEngine:
    def __init__(self):
        self.db = SupabaseClient()
        self.category_map = self.db.get_category_map()
        log.info(f"SyncEngine ready: {len(self.category_map)} merchants loaded")

    def categorize(self, merchant, amount):

        if merchant in self.category_map:
            log.debug(f"Exact match: {merchant}")
            return self.category_map[merchant]

        close = get_close_matches(merchant, self.category_map.keys(), n=1, cutoff=0.75)

        if close:
            log.debug(f"Fuzzy match: {merchant} -> {close[0]}")
            return self.category_map[close[0]]
        
        result = ask_ollama(merchant, amount)
        if result:
            log.info(f"Ollama categorized: {merchant} -> {result}")
            return result
        
        log.warning(f"Unknown merchant: {merchant}")
        return {"type": "Expenses", "category": "Uncategorized"}
    

    def process_sms(self, sms_body:str, sms_id: str = None) -> dict:
        parsed = parse_sms(sms_body)
        if not parsed:
            log.error(f"Parsed failed: {sms_body[:50]}")
            if sms_id:
                self.db.client.table('sms_raw').update(
                    {'status': 'failed'}
                ).eq('id', sms_id).execute()
            return None
        
        category_info = self.categorize(
            parsed['merchant_name'],
            float(parsed['amount'])
        )

        raw_ts = parsed['timestamp']
        dt = datetime.strptime(raw_ts, "%d-%m-%y, %H:%M:%S")
        iso_ts = dt.isoformat()

        transaction = {
            'sms_id': sms_id,
            'amount': float(parsed['amount']),
            'merchant_name': parsed['merchant_name'],
            'type': category_info['type'],
            'category': category_info['category'],
            'transaction_id': parsed['transaction_id'],
            'timestamp': iso_ts,
            'account_number': parsed.get('account_number', '')
        }

        self.db.insert_transaction(transaction)
        # 5. Write to Excel
        add_to_excel({
            **transaction,
            'timestamp': raw_ts
        })

        if sms_id:
            self.db.client.table('sms_raw').update(
                {'status': 'processed'}
            ).eq('id', sms_id).execute()
        
        log.info(f"✓ Processed: {parsed['merchant_name']} ₹{parsed['amount']}")
        return transaction
    

    def process_pending(self) -> dict:
        try:
            response = self.db.client.table('sms_raw')\
            .select('*')\
            .eq('status', 'new')\
            .execute()
        
            sms_list = response.data
            log.info(f"Pending SMS found: {len(sms_list)}")
        
            success, failed = 0, 0
        
            for sms in sms_list:
                try:
                    result = self.process_sms(sms['sms_body'], sms['id'])
                    if result:
                        success += 1
                    else:
                        failed += 1
                except Exception as e:
                    log.error(f"Failed: {sms['id']} - {e}")
                    failed += 1
            log.info(f"Batch done: {success} processed, {failed} failed")
            return {'success': success, 'failed': failed}
    
        except Exception as e:
            raise SupabaseConnectionError(f"process_pending failed: {e}")


if __name__ == "__main__":
    try:
        engine = SyncEngine()
        print("✓ SyncEngine initialized")
    except Exception as e:
        print(f"Error: {e}")
        exit()

    # Only this:
    result = engine.process_pending()
    print(f"Pending result: {result}")