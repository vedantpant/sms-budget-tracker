# SMS Budget Tracker — SESSION_CONTEXT_2.md
# Phase 4 Start Point

---

## ✅ COMPLETED

### Phase 1: Foundation
- `config.py` — Config class, loads from .env
- `exceptions.py` — 15+ custom exception classes
- `logger.py` — log object, rotating file + console
- `utils.py` — CircuitBreaker, retry decorator, generate_sms_hash
- `validators.py` — input sanitization

### Phase 2: Supabase Client (`supabase_client.py`)
- `SupabaseClient` class with `Config.SUPABASE_URL`, `Config.SUPABASE_KEY`
- `CircuitBreaker(name='supabase', threshold=5, timeout=300)`
- `insert_sms_raw(sms_body, sender)` — hash duplicate detection
- `get_category_map()` → dict {merchant: {category, type}}
- `insert_transaction(data)` — txn_id duplicate detection
- `migrate_category_map()` — JSON → Supabase (source='import')
- `migrate_excel()` — Excel row 12+ → Supabase

**Data migrated:**
- 171 merchants in `category_map` table
- 478 transactions in `transactions` table

### Phase 3: Sync Engine (`sync_engine.py`)
- `SyncEngine` class
- `__init__()` — creates SupabaseClient, loads category_map
- `categorize(merchant, amount)` — 4 layers:
  - Layer 1: Exact match from self.category_map
  - Layer 2: Fuzzy match (difflib, cutoff=0.75)
  - Layer 3: Ollama (ask_ollama from ai_categorizer.py)
  - Layer 4: Returns {'type': 'Expenses', 'category': 'Uncategorized'}
- `process_sms(sms_body, sms_id)` — full pipeline:
  1. parse_sms() from parser.py
  2. categorize()
  3. insert_transaction() to Supabase
  4. add_to_excel() from openpyxl_basic.py (win32com, preserves formatting)
  5. Update sms_raw status → 'processed' or 'failed'
- `process_pending()` — fetches status='new' from sms_raw, processes each

---

## 🗄️ SUPABASE TABLES

### `sms_raw`
```
id, sms_body, sms_hash, sender, status, retry_count, source, error_message, created_at, processed_at
status allowed: 'new', 'processed', 'failed', 'pending'
source allowed: 'manual', 'ollama', 'import'
```

### `transactions`
```
id, sms_id, amount, merchant_name, type, category, transaction_id, timestamp, account_number, created_at
```

### `category_map`
```
merchant_name (PK), type, category, source, created_at
source allowed: 'manual', 'ollama', 'import'
```

### `error_log`
```
id, component, error_type, error_message, retry_count, sms_raw_id, transaction_id, created_at, resolved_at
```

### `audit_trail`
```
id, table_name, record_id, action, old_values, new_values, changed_by, created_at
```

---

## 📁 PROJECT STRUCTURE

```
D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\
├── config.py              ← Config class
├── exceptions.py          ← Custom exceptions
├── logger.py              ← log object
├── utils.py               ← CircuitBreaker, retry, generate_sms_hash
├── validators.py          ← Input sanitization
├── supabase_client.py     ← SupabaseClient class ✅
├── sync_engine.py         ← SyncEngine class ✅
├── parser.py              ← parse_sms(), get_category(), process_sms()
├── ai_categorizer.py      ← ask_ollama(), categorize_merchant()
├── openpyxl_basic.py      ← add_to_excel(), win32com Excel writer
├── main.py                ← old entry point (not used)
├── bulk_import.py         ← old bulk import (not used)
├── dashboard.py           ← Streamlit dashboard (Phase 5)
├── smart_commit.py        ← AI commit messages via Ollama
├── CATEGORY_MAP.json      ← 171 merchants (source of truth = Supabase now)
└── Ultimate Personal Budget Manager.xlsx
```

---

## ⚠️ KNOWN ISSUES / NOTES

1. **openpyxl warnings** — "Unknown extension not supported" — harmless, ignore
2. **win32com required** — `openpyxl_basic.py` uses win32com, Windows only
3. **Timestamp format** — parser returns "DD-MM-YY, HH:MM:SS", sync_engine converts to ISO for Supabase but passes raw_ts to add_to_excel()
4. **Test SMS in sms_raw** — One fake SMS (id: 4e079a7f) with status='failed', non-parseable format — ignore
5. **CATEGORY_MAP.json** — Still used by parser.py directly. sync_engine.py loads from Supabase instead.

---

## 🔄 CURRENT END-TO-END FLOW

```
[Manual/Phone SMS]
       ↓
  sms_raw table (status='new')
       ↓
  process_pending() ← manually run for now
       ↓
  parse_sms() → categorize() → insert_transaction() → add_to_excel()
       ↓
  sms_raw status → 'processed'
```

---

## 🎯 PHASE 4: listener.py (NEXT)

### What to build:
A background service that:
1. Polls Supabase `sms_raw` every 30 seconds for status='new'
2. Calls `engine.process_pending()` automatically
3. Graceful shutdown on SIGINT/SIGTERM (Ctrl+C)
4. Auto-restart on crash
5. Heartbeat logging (every N cycles)
6. Windows Task Scheduler config for auto-start on boot

### File: `listener.py`

```python
# Structure:
class Listener:
    def __init__(self):
        self.engine = SyncEngine()
        self.running = False
        self.poll_interval = 30  # seconds
        self.heartbeat_every = 10  # cycles

    def start(self):           # main loop
    def stop(self):            # graceful shutdown
    def _poll(self):           # single poll cycle
    def _heartbeat(self):      # log status

# Entry point:
if __name__ == "__main__":
    listener = Listener()
    listener.start()
```

### Signal handling:
```python
import signal
signal.signal(signal.SIGINT, lambda s, f: listener.stop())
signal.signal(signal.SIGTERM, lambda s, f: listener.stop())
```

### Windows Task Scheduler:
- Trigger: At startup
- Action: `python D:\...\listener.py`
- Restart on failure: Yes

---

## ⬜ REMAINING PHASES

```
Phase 4: listener.py          ← START HERE
Phase 5: Dashboard upgrades   ← health panel, error queue, manual categorize UI
Phase 6: Telegram alerts      ← notify on failures/transactions
Phase 7: Testing suite        ← pytest, >80% coverage
Phase 8: Phone SMS setup      ← SMS Forwarder app → Supabase
Phase 9: CI/CD + polish       ← GitHub Actions, README
```

### Phase 8 Note:
- Use **SMS Forwarder** app (Play Store) OR **MacroDroid**
- Configure: AXISBK SMS → HTTP POST → Supabase REST API
- Do AFTER Phase 4 so listener auto-processes incoming SMS
- Supabase REST endpoint for insert:
  `POST https://[project].supabase.co/rest/v1/sms_raw`

---

## 🔧 CONFIG KEYS (from .env)

```
SUPABASE_URL=https://wxwdazdeahobediwcwdr.supabase.co
SUPABASE_KEY=eyJhbGc...
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
CATEGORY_MAP_FILE=CATEGORY_MAP.json
EXCEL_FILE=Ultimate Personal Budget Manager.xlsx
```

---

## 📌 HOW TO START NEXT SESSION

1. Upload this file + `sync_engine.py` + `supabase_client.py`
2. Say: "Continue Phase 4 — listener.py"
3. Claude will start from Phase 4 Step 1
