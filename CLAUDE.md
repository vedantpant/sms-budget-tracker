# SMS Budget Tracker — CLAUDE.md
# Project Context for Claude Code

> **HOW TO USE THIS FILE:**
> - Feed this file to Claude Code at session start: `/add CLAUDE.md`
> - Claude Code should read the project directory before making changes
> - Update the `## CURRENT STATUS` section when a task is completed
> - Always ask user for input before making destructive changes
> - Never exhaust tokens — work in small focused chunks
> - When a phase is complete, mark it ✅ and update `## NEXT UP`

---

## PROJECT OVERVIEW

**Name:** Ultimate Personal Budget Manager (app_tracker)
**Stack:** Python, Supabase, Excel (win32com), Ollama (llama3.1:8b)
**Goal:** Auto-sync Axis Bank SMS → Supabase → Excel tracker

**Project Path:**
```
D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\
```

---

## PROJECT STRUCTURE

```
app_tracker/
├── config.py              ← Config class, loads .env
├── exceptions.py          ← 15+ custom exceptions
├── logger.py              ← Rotating file + console logger
├── utils.py               ← CircuitBreaker, retry, generate_sms_hash
├── validators.py          ← Input sanitization
├── supabase_client.py     ← SupabaseClient class
├── sync_engine.py         ← SyncEngine — core processing logic
├── parser.py              ← parse_sms(), get_category(), process_sms()
├── ai_categorizer.py      ← ask_ollama(), categorize_merchant()
├── openpyxl_basic.py      ← add_to_excel(), add_bulk_to_excel() via win32com
├── listener.py            ← Background polling service
├── bulk_import.py         ← One-time bulk SMS import from all_sms.json
├── fix_excel_missing.py   ← One-time fix for Excel missing transactions
├── dashboard.py           ← Streamlit dashboard (Phase 5 — pending)
├── smart_commit.py        ← AI commit messages via Ollama
├── all_sms.json           ← Exported phone SMS (from Termux)
├── CATEGORY_MAP.json      ← 201 merchants (backup — source of truth = Supabase)
└── Ultimate Personal Budget Manager.xlsx
```

---

## SUPABASE TABLES

```
sms_raw         → id, sms_body, sms_hash, sender, status, retry_count, source, error_message, created_at, processed_at
transactions    → id, sms_id, amount, merchant_name, type, category, transaction_id, timestamp, account_number, created_at
category_map    → merchant_name (PK), type, category, source, created_at
error_log       → id, component, error_type, error_message, retry_count, sms_raw_id, transaction_id, created_at, resolved_at
audit_trail     → id, table_name, record_id, action, old_values, new_values, changed_by, created_at
```

**Supabase URL:** `https://wxwdazdeahobediwcwdr.supabase.co`

---

## END-TO-END FLOW

```
Phone SMS (AXISBK) 
    ↓
SMS Forwarder App (Android) → POST → Supabase sms_raw (status='new')
    ↓
listener.py (polls every 60s) → process_pending()
    ↓
parse_sms() → categorize() → insert_transaction() → add_to_excel()
    ↓
sms_raw status → 'processed'
```

---

## COMPLETED PHASES ✅

### Phase 1 — Foundation ✅
- `config.py`, `exceptions.py`, `logger.py`, `utils.py`, `validators.py`

### Phase 2 — Supabase Client ✅
- `supabase_client.py` — insert_sms_raw, get_category_map, insert_transaction
- Data migrated: 171+ merchants in category_map, 600+ transactions

### Phase 3 — Sync Engine ✅
- `sync_engine.py` — categorize (4 layers), process_sms, process_pending
- Duplicate detection via transaction_id + sms_hash

### Phase 4 — Listener ✅
- `listener.py` — polling every 60s, heartbeat every 10 cycles, graceful shutdown
- Signal handling (SIGINT/SIGTERM)
- Windows Task Scheduler configured (auto-start at logon)

### Phase 8 — SMS Forwarder Setup ✅
- SMS Forwarder app installed on Android
- Filter: `*AXISBK*` (wildcard), Forward by Conditions
- Webhook: POST to Supabase REST API
- `{msg}` → sms_body, `{in-number}` → sender
- OTP & security messages forwarding enabled
- Notification access granted

### Parser Fixes ✅
- UPI debit SMS ✅
- OUTWARD REM ✅
- Credited salary SMS ✅ (with/without 'on')
- NACH debit (Groww Pay SIPs) ✅
- Google Play auto debit ✅
- Auto Pay processed ✅

### Excel Fixes ✅
- win32com retry logic (3 retries, 3s delay)
- `excel.Visible = False`, `excel.DisplayAlerts = False`
- `fix_excel_missing.py` — one-time sync from Supabase → Excel

### Category Map Fixes ✅
- 201 merchants in Supabase category_map
- Added: INDMoney, INDmoney, Jio Prepaid Recharg, SALMAN S, GADGET TECHNOLOGIES,
  Malabar Gold Pvt Lt, Google Play, GOOGLEPLAY, Groww Pay Services P,
  AIRBNB PAYMENTS IND, CLICK2RACE PRIVATE, MC DONALDS, WESTSIDE, UNDER ARMOUR,
  EBADI PERFUMES, and 15+ more

---

## 🔄 CURRENT STATUS

### Phase 5 — Dashboard (Streamlit) ✅ COMPLETED

**Part 1 — Data source refactor ✅ COMPLETED**
- Migrated from Excel-based dashboard to Supabase-first architecture
- Updated `load_transactions()` to read from Supabase transactions table
- 60-second cache TTL for real-time updates
- Error handling returns empty list on failure

**Part 2 — Health Panel ✅ COMPLETED**
- Added 3 health data loader functions (30s cache TTL):
  - `get_listener_status()` — last processed SMS timestamp
  - `get_pending_sms_count()` — SMS waiting to be processed
  - `get_recent_errors()` — recent errors from error_log
- System Health panel displays 4 metrics:
  - Listener Status with color indicators (🟢 Just now / 🟡 Xh ago / 🔴 Never)
  - Pending SMS count (counts sms_raw.status='new')
  - Last Sync timestamp (HH:MM:SS format)
  - Recent Errors with expandable error details
- Tested and working — dashboard shows all metrics correctly
- 625 transactions loaded from Supabase

**Part 3 — Error Queue Viewer ✅ COMPLETED**
- Fetches failed SMS from sms_raw table (status='failed')
- Displays up to 5 failed SMS in expandable cards
- Shows full SMS body, error message, status, retry count, source
- Retry button to re-queue SMS (changes status to 'new', increments retry_count)
- Dashboard auto-refreshes on retry
- Shows success message if no failed SMS exist

**Part 4 — Manual Categorization UI ✅ COMPLETED**
- Fetches uncategorized transactions from database
- Displays up to 10 uncategorized transactions in expandable cards
- Shows: merchant name, amount, type, date, transaction ID, current category
- Dropdown to select correct category (pulls from category_map)
- Save button to update transaction category in Supabase
- Real-time confirmation and dashboard refresh on save
- Shows success message if all transactions are categorized

**Dashboard Features Summary:**
- ✅ Real-time transaction data from Supabase (625 transactions)
- ✅ System health monitoring (listener status, pending SMS, last sync, recent errors)
- ✅ Error queue with retry capability
- ✅ Manual categorization for uncategorized transactions
- ✅ Category breakdown with visual progress bars
- ✅ Top 5 merchants with transaction counts and averages
- ✅ Expense distribution pie chart
- ✅ Monthly expense trend bar chart
- ✅ AI-powered insights (Ollama integration)
- ✅ HTML report export with charts and tables

---

### Phase 4.5 — Parser Refactor (Layered + Learning) ✅ COMPLETED

**Root Cause:** Multiple SMS formats exist (and will change). Rather than hardcode patterns, build a learning system.

**New Approach: Layered Fallback + Learning**
```
1. Try specific patterns (HIGH confidence)
   - UPI Credit, ACH/Salary, etc.
2. Try generic fallback (MEDIUM confidence)
   - Flexible: extract amount + account + timestamp
3. If NONE match → Log as UNMATCHED
   - Track patterns we don't understand yet
   - Review periodically to add new patterns
```

**Implementation — COMPLETED:**
- ✅ Step 1: Created `sms_test_data.json` — documented all 7 SMS formats + 324 AXISBK SMS
- ✅ Step 2: Created `parser_test.py` — tests all patterns, shows coverage
- ✅ Step 3: Fixed `parser.py` — regex now handles credit without 'on' keyword
- ✅ Step 4: Updated test expectations — "ignore" cases now handled correctly
- ✅ Step 5: **100% test coverage** — all 14 test cases pass

**Test Results:**
```
✅ PASSED: 14/14 tests
❌ FAILED: 0 tests
📊 Coverage: 100.0%
```

**Parser Fix Applied:**
```
OLD: r'...(\d{2}-\d{2}-\d{2})\s+at\s+(\d{2}:\d{2}:\d{2})'  ← Needs TWO "at"
NEW: r'...(\d{2}-\d{2}-\d{2}),?\s+(?:at\s+)?(\d{2}:\d{2}:\d{2})'  ← Optional comma, optional second "at"
```

**Missing Transactions (NOW FIXED):**
- ✅ June 2 → ₹57416.76 (format: "...at 02-06-26 11:47:06 IST\nRef: IMPS/P2A...") — **PARSER NOW HANDLES THIS**

**Issues Resolved:**
- ✅ Issue 1: Credited SMS without 'on' keyword — Parser regex fixed + 100% test coverage
- ✅ Issue 2: Missing June 2 transaction (₹57416.76) — Parser now handles this format
- ✅ Issue 3: INDMoney → type='Savings', category='Stock Portfolio' (10 transactions fixed)
- ✅ Issue 4: Suresh Krishana, KULANTHAIVELU PURUS → type='Expenses', category='Food Outside' (2 transactions fixed)

**All Critical Issues RESOLVED! 🎉**

---

## ⬜ REMAINING PHASES

### Phase 6 — Telegram Alerts ⬜
- Notify on transaction processed
- Notify on parse failures
- Daily summary

### Phase 7 — Testing Suite ⬜
- pytest setup
- Unit tests for parser.py (all SMS formats)
- Unit tests for sync_engine.py
- Integration tests
- Target: >80% coverage

### Phase 9 — CI/CD + Polish ⬜
- GitHub Actions
- README.md
- .env.example
- Proper logging levels
- Error recovery improvements

---

## KNOWN ISSUES / NOTES

1. **openpyxl warnings** — "Unknown extension not supported" — harmless
2. **win32com** — Windows only, Excel must not be open during writes
3. **Timestamp format** — parser returns "DD-MM-YY, HH:MM:SS", sync_engine converts to ISO for Supabase
4. **CATEGORY_MAP.json** — backup only, Supabase is source of truth now
5. **all_sms.json** — covers Oct 2025 to May 2026 (from Termux export)
6. **sms_hash** — column is now nullable (fixed for SMS Forwarder direct inserts)
7. **Duplicate protection** — 3 layers: sms_hash, transaction_id, Excel get_existing_transactions()
8. **Failed SMS** — auto-marked as 'failed' in sms_raw after exception (no more infinite retries)

---

## CONFIG KEYS (.env)

```
SUPABASE_URL=https://wxwdazdeahobediwcwdr.supabase.co
SUPABASE_KEY=eyJhbGc...
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
CATEGORY_MAP_FILE=CATEGORY_MAP.json
EXCEL_FILE=Ultimate Personal Budget Manager.xlsx
```

---

## CLAUDE CODE INSTRUCTIONS

**Core Philosophy:** Design for learning + adaptability. The parser should teach us about SMS patterns, not just extract data.

When working on this project:

1. **Always read files before editing** — use Read tool on relevant files
2. **Work in small chunks** — one function/fix at a time
3. **Test before moving on** — run quick python -c tests
4. **Ask before destructive ops** — SQL UPDATEs, file overwrites
5. **Ask before making changes** — get user approval on approach first
6. **Update this file** — mark issues resolved, update CURRENT STATUS
7. **Commit after each fix** — `python smart_commit.py`

**Parser Design Philosophy:**
- Specific patterns first (high confidence)
- Generic fallback second (catches unknowns)
- Log unmatched SMS (learn from failures)
- Build test suite (document patterns)
- Track coverage (show progress)

**Test Infrastructure (Phase 4.5):**
- `sms_test_data.json` — Live documentation of all SMS formats seen (324 AXISBK SMS analyzed)
- `parser_test.py` — Automated test suite that runs against test data
- `unmatched_sms.json` — Log of SMS that don't match any pattern (for review)
- Coverage report — 14 test cases, 100% pass rate = confidence in parser

When new SMS format appears:
1. Add example to `sms_test_data.json`
2. Run `python parser_test.py`
3. If it fails, add new regex pattern to `parser.py`
4. Re-run test until it passes
5. Commit with smart_commit.py

### Start each session with:
```
1. Read CLAUDE.md (this file)
2. Check current issues section
3. Ask user: "Which issue should we tackle first?"
4. Fix → Test → Commit → Update CLAUDE.md
```

### Parser SMS formats reference:
```python
# UPI Debit
"INR 645.00 debited\nA/c no. XX0316\n20-04-26, 18:24:43\nUPI/P2M/502760971106/CALIFORNIA BURRITO"

# OUTWARD REM
"Debit INR 19904.58\nAxis Bank A/c XX0316\n20-04-26 10:05:31\nOUTWARD REM NO. 0741RI2611"

# Credited (with 'on')
"INR 174445.00 credited to A/c no. XX0316 on 30-03-26 at 12:24:19 IST. Info - ACH-CR-SAL-ENPHASESOLARENE"

# Credited (without 'on')
"INR 57416.76 credited to A/c no. XX0316 at 02-06-26 11:47:06 IST"

# NACH Debit (SIP)
"NACH debit towards Groww Pay Services P for INR 2,700.00 with UMRN UTIB7022402220010690 has been successfully processed in A/c no. XX0316 today - Axis Bank"

# Google Play
"INR 130.00 for Google Play will be auto debited via Axis Bank"
"Auto Pay of INR 130.00 for GOOGLEPLAY has been processed"
```
