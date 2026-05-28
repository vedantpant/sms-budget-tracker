# SMS Budget Tracker — Complete Context & Continuation Guide

## Project Owner
- **Name:** Vedant Pant
- **Role:** Senior SDET at Enphase Energy, Bengaluru
- **Communication:** Hinglish (Hindi-English mix), casual, prefers direct honest feedback
- **Learning style:** Hands-on, one concept at a time, wants to write code himself (guide, don't give full code), micro-step approach works best
- **Important:** He said "mujhe khud banana hai, sirf guide karo!" — guide step by step, let him write and run, check output, then next step

---

## Project Overview

**One-line:** Phone pe bank SMS aaye → automatically track ho jaaye ki kitna kharch hua, kahan hua, kaunsi category mein gaya → Excel + Dashboard mein dikh jaaye.

**GitHub:** https://github.com/vedantpant/sms-budget-tracker

**Stack:** Python 3.13, openpyxl, Ollama (llama3.1:8b), Streamlit, Plotly, Supabase, Axis Bank SMS

---

## Current Project Structure

```
D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\
├── main.py                 ← entry point (single SMS test)
├── bulk_import.py          ← bulk process all SMS from JSON
├── parser.py               ← SMS regex parsing + 4-layer categorization
├── ai_categorizer.py       ← Ollama LLM integration for merchant categorization
├── openpyxl_basic.py       ← Excel read/write via openpyxl (NOT win32com despite old name)
├── summary_report.py       ← Terminal monthly report with AI insights
├── dashboard.py            ← Streamlit interactive dashboard + HTML export
├── smart_commit.py         ← AI-powered git commit message generator
├── config.py               ← Centralized configuration (NEW - Phase 1)
├── exceptions.py           ← Custom exception hierarchy, 15+ classes (NEW - Phase 1)
├── logger.py               ← Rotating file + console logging (NEW - Phase 1)
├── utils.py                ← Retry decorator, circuit breaker, hash generator (NEW - Phase 1)
├── validators.py           ← Input sanitization & validation (NEW - Phase 1)
├── CATEGORY_MAP.json       ← 170+ merchant → category mappings (auto-grows)
├── all_sms.json            ← Raw SMS dump from Termux (2000 SMS, 649 Axis Bank)
├── Ultimate Personal Budget Manager.xlsx  ← Main Excel with 480 transactions
├── .env                    ← Secrets: SUPABASE_URL, SUPABASE_KEY, OLLAMA_URL (gitignored)
├── .gitignore              ← Ignores .env, *.log, all_sms.json, *.xlsx
├── README.md
└── ROADMAP.md              ← 9-phase implementation plan
```

---

## Detailed File Descriptions & Current Code State

### 1. `parser.py` — Core SMS Processing

**4 regex patterns:**
- UPI debit: `INR X.XX debited...UPI/P2M/txn_id/merchant`
- NEFT debit: `Debit INR X.XX...OUTWARD REM NO. xxx`
- Salary credit: `INR X.XX credited to A/c...`
- ACH debit: `Debit INR X.XX...ACH-DR-xxx`

**Key functions:**
- `parse_sms(sms)` → returns dict {amount, account_number, timestamp, transaction_id, merchant_name} or None
- `get_category(merchant, amount=0)` → 4-layer lookup: exact → fuzzy (difflib, cutoff=0.75) → Ollama → manual
- `handle_unknown_merchant(merchant_name, amt=0)` → calls categorize_merchant from ai_categorizer, falls back to manual terminal input
- `process_sms(sms)` → glue: parse + categorize → returns complete transaction dict

**Important:** `MERCHANT_CATEGORY_MAP` is loaded at module level from CATEGORY_MAP.json. `get_category` also updates in-memory dict when new merchants are categorized (fix applied during session).

**157 SMS remain unparsed** — mandates, OTPs, deposits, Jar Gold debits. These need either new regex patterns or AI parsing (future feature).

### 2. `ai_categorizer.py` — Ollama Integration

**Key functions:**
- `ask_ollama(merchant_name, amount)` → sends prompt to Ollama localhost:11434, returns dict {type, category} or None
- `categorize_merchant(merchant_name, amount)` → calls ask_ollama, shows suggestion, asks user confirmation (y/n), saves to CATEGORY_MAP.json if confirmed, returns result or None

**Prompt uses few-shot examples** (5 examples of merchant→category mappings in the prompt). This improved accuracy from 1/5 to 5/5.

**Model:** llama3.1:8b (4.7GB, installed via `ollama pull llama3.1:8b`). 3b was tested but too inaccurate (3/5).

**Test code is wrapped in `if __name__ == "__main__":` to prevent execution on import.**

### 3. `openpyxl_basic.py` — Excel Operations

- `add_to_excel(transaction)` — adds single transaction row to "Budget Tracking" sheet
- `add_bulk_to_excel(transactions)` — adds multiple transactions, has duplicate detection via transaction_id
- Excel structure: 6 sheets (Settings, Budget Planning, Budget Tracking, Budget Dashboard, Calculations, Dropdown Data)
- Data starts at row 8 in Budget Tracking (rows 1-7 are headers/formatting)
- Columns: C=Date, D=Type, E=Category, F=Amount, G=Merchant+TransactionID

### 4. `summary_report.py` — Terminal Report

Reads Excel → groups by month → shows:
- Month-wise totals (Expenses/Income/Savings)
- Category breakdown with bar visualization for latest complete month
- Top 5 merchants by spending
- Month-over-month comparison (% change)
- AI Insights via Ollama (3 bullet points of spending advice)

### 5. `dashboard.py` — Streamlit Dashboard

**Run:** `streamlit run dashboard.py` → opens localhost:8501

**Features implemented:**
- Sidebar: month selector dropdown, transaction count
- Metric cards: Total Expenses, Income, Savings, Transaction count
- Category breakdown with progress bars
- Top 5 merchants with transaction frequency
- Plotly pie chart (donut) for expense distribution
- Plotly bar chart for monthly expense trend
- AI Insights button (generates via Ollama on click)
- HTML Export button — generates standalone .html report with Chart.js charts, downloadable

**Data loading uses `@st.cache_data` for performance.**

### 6. `smart_commit.py` — AI Git Commit Tool

**Run:** `python smart_commit.py`

**Flow:** git status → show changed files → ask stage (y/n/select) → git diff → Ollama generates commit message → user confirms/edits → commit → optional push

**Known issue:** Ollama times out on large diffs (>3000 chars). Fallback: manual commit.

**Uses `encoding="utf-8", errors="replace"` in subprocess to handle ₹ symbol on Windows.**

### 7. `config.py` — Configuration

All settings centralized. Uses `python-dotenv` to load .env file. Key settings: SUPABASE_URL/KEY, OLLAMA_URL/MODEL/TIMEOUT, file paths, retry settings (MAX_RETRIES=3, DELAY=5, BACKOFF=2), circuit breaker (THRESHOLD=5, TIMEOUT=300), POLL_INTERVAL=30, FUZZY_MATCH_CUTOFF=0.75.

### 8. `exceptions.py` — Error Hierarchy

```
BudgetTrackerError (base)
├── TransportError
│   ├── SupabaseConnectionError
│   └── SupabaseTimeoutError
├── ParsingError
│   ├── UnknownSMSFormatError (stores sms_body[:100])
│   ├── InvalidAmountError
│   └── MissingFieldError (stores field name)
├── CategorizationError
│   ├── OllamaConnectionError
│   ├── OllamaTimeoutError
│   ├── OllamaInvalidResponseError
│   └── CategoryNotFoundError (stores merchant name)
├── StorageError
│   ├── ExcelWriteError
│   │   ├── ExcelLockedError
│   │   └── ExcelCorruptError
│   └── CategoryMapWriteError
├── DuplicateError
│   ├── DuplicateSMSError (stores hash)
│   └── DuplicateTransactionError (stores txn_id)
├── NetworkError
│   └── RetryExhaustedError (stores component + max_retries)
└── CircuitBreakerOpenError (stores component)
```

### 9. `logger.py` — Logging

Global logger instance: `from logger import log`
- Console: INFO+ level, format: `HH:MM:SS | LEVEL | message`
- File: DEBUG+ level, rotating 5MB × 3 backup files, format includes date + module name

### 10. `utils.py` — Utilities

- `retry(max_retries, delay, backoff, exceptions)` — decorator for automatic retry with exponential backoff
- `CircuitBreaker(name, threshold, timeout)` — class with CLOSED/OPEN/HALF_OPEN states
- `generate_sms_hash(sms_body)` — MD5 hash for duplicate SMS detection
- `to_ist(utc_time)` / `to_utc(ist_time)` — timezone converters

### 11. `validators.py` — Input Validation

**NOTE: File is named `validators.py` (plural) because `validator` conflicts with a pip package.**

- `sanitize_sms(sms_body)` — removes control chars, trims, enforces max 1000 chars, min 10 chars
- `validate_amount(amount_str)` — parses amount, checks positive, checks <10M
- `validate_merchant(merchant_name)` — removes SQL injection chars (;'"\\), max 100 chars
- `validate_category(type_name, category_name)` — validates type is Expenses/Income/Savings

---

## Supabase Setup (COMPLETED)

**Project:** sms-budget-tracker
**Region:** South Asia (Mumbai) — ap-south-1
**Project ID:** wxwdazdeahobediwcwdr
**Project URL:** https://wxwdazdeahobediwcwdr.supabase.co
**Python client:** `supabase` package installed, connection tested, CRUD working

### Database Tables (5 created):

```sql
-- 1. sms_raw: Raw SMS storage with duplicate detection
CREATE TABLE sms_raw (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sms_body TEXT NOT NULL,
    sms_hash TEXT UNIQUE NOT NULL,        -- MD5 hash, Level 1 duplicate check
    sender TEXT DEFAULT 'AXISBK',
    status TEXT DEFAULT 'new',            -- new/processed/failed/pending
    retry_count INT DEFAULT 0,
    source TEXT DEFAULT 'sync',           -- sync/bulk_import/manual
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- 2. transactions: Processed transactions
CREATE TABLE transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sms_id UUID REFERENCES sms_raw(id),
    amount DECIMAL(12,2) NOT NULL,
    merchant_name TEXT NOT NULL,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    transaction_id TEXT UNIQUE,           -- Level 2 duplicate check
    timestamp TIMESTAMPTZ,
    account_number TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. category_map: Cloud version of CATEGORY_MAP.json
CREATE TABLE category_map (
    merchant_name TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    source TEXT DEFAULT 'manual',         -- manual/ollama/import
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. error_log: Error tracking
CREATE TABLE error_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    component TEXT NOT NULL,
    error_type TEXT NOT NULL,
    error_message TEXT,
    sms_id UUID REFERENCES sms_raw(id),
    retry_count INT DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. audit_trail: Change tracking
CREATE TABLE audit_trail (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    action TEXT NOT NULL,
    table_name TEXT NOT NULL,
    record_id TEXT,
    old_value JSONB,
    new_value JSONB,
    performed_by TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**RLS Policies:** "Allow all" policies created for all 5 tables (personal project).

---

## Technical Decisions Made & Why

1. **Ollama over Claude API** — Free, local, no API costs. Vedant specifically wanted to avoid API costs.
2. **llama3.1:8b over 3b** — Tested both. 3b got 3/5 accuracy, 8b got 5/5. Model size matters for instruction following.
3. **Few-shot prompting** — Added 5 examples to the Ollama prompt. Improved accuracy from 1/5 (no examples) to 5/5.
4. **scikit-learn ML was tried and abandoned** — TF-IDF + Naive Bayes (50% accuracy) and SVM (55.8% accuracy) both failed due to class imbalance (94/167 = Food Outside) and uninformative features (person names like "MOHAMMED RAFIQ" carry no category signal). This was a valuable learning experience, not wasted effort.
5. **4-layer categorization** — Exact match (free, instant) → Fuzzy match (free, instant) → Ollama (2-3 sec, free) → Manual input. Each layer is a fallback for the previous.
6. **Self-improving CATEGORY_MAP** — Every new merchant categorized (by Ollama or manually) is saved to CATEGORY_MAP.json. Over time, fewer Ollama calls needed.
7. **Supabase over Firebase** — Open source, PostgreSQL (industry standard), better learning value. Firebase was originally chosen but pivoted to Supabase.
8. **Method D (Hybrid) for sync** — Cloud processing for known merchants (90%), laptop Ollama for unknown merchants (10%). Best of both worlds.
9. **`validators.py` not `validator.py`** — Naming conflict with pip `validator` package caused ImportError. Renamed to `validators.py`.

---

## ML Journey (Important for Vedant's Learning)

1. Loaded CATEGORY_MAP.json → 167 samples, 18 categories
2. Analyzed distribution → Food Outside: 94 (56%), 6 categories with only 1 sample
3. TF-IDF + MultinomialNB → 50% accuracy (predicted "Food Outside" for everything)
4. TF-IDF + LinearSVC (class_weight='balanced') → 55.8% (slightly better, caught Utilities + Stock Portfolio)
5. Char n-grams (2,4) + LinearSVC → 52.9% (worse — char patterns didn't help)
6. **Root cause identified:** Person names (MOHAMMED RAFIQ, VANSHIKA MITTAL) carry zero category signal. No text-based ML can solve this.
7. **Pivoted to Ollama LLM** — world knowledge enables categorization even for ambiguous merchants.
8. This journey is valuable for interviews: "I tried ML, analyzed why it failed, then pivoted to a better approach."

---

## Edge Cases & Error Handling Strategy Designed

### Duplicate Detection (3 levels):
1. **SMS level:** MD5 hash of sms_body → UNIQUE in sms_raw table
2. **Transaction level:** transaction_id (UPI ref number) → UNIQUE in transactions table
3. **Excel level:** Existing duplicate check in openpyxl_basic.py

### Fallback Chain per Component:
- **SMS Transport:** SMS Forwarder retry → SMS stays on phone → Termux bulk export → Manual copy-paste
- **Cloud Storage (Supabase):** Retry → Extended outage = Termux backup → Local SQLite cache
- **Parsing:** 4 regex patterns → Extended regex → Ollama parse → Mark "parse_failed"
- **Categorization:** Exact match → Fuzzy → Ollama → Mark "pending" → Manual → "Uncategorized" default
- **Excel Write:** Retry 3x → Excel locked? Wait 5s → Corrupt? Backup file → Fail? Data safe in Supabase
- **Ollama:** Retry 3x → Connection refused? Try after delay → All fail? Mark "pending"
- **Network:** Exponential backoff (5s→10s→20s) → Offline? SQLite cache → Online? Flush cache
- **Script Crash:** Try-except top level → Task Scheduler auto-restart → Max 5 restarts → Alert

### Circuit Breaker Pattern:
- After 5 consecutive failures → OPEN state (stop calling for 5 min)
- After 5 min → HALF_OPEN (try one test call)
- Success → CLOSED (resume normal)
- Prevents wasting resources on a failing service

---

## Architecture — Target State (Method D Hybrid)

```
📱 Phone (SMS Forwarder app - FREE)
    │ SMS from AXISBK detected
    │ HTTP POST (automatic)
    ▼
☁️ Supabase (PostgreSQL cloud DB - FREE tier)
    ├── sms_raw table (raw SMS stored, deduplicated by hash)
    ├── Edge Function (FUTURE): auto-categorize known merchants
    │   ├── Known merchant → processed instantly, no laptop needed
    │   └── Unknown merchant → status='pending'
    ▼
💻 Laptop (Python listener, auto-starts on boot via Task Scheduler)
    ├── Polls Supabase every 30 sec for status='new' or 'pending'
    ├── parse_sms() → regex extract fields
    ├── get_category() → 4-layer: exact→fuzzy→Ollama→manual
    ├── Save to Supabase transactions table
    ├── Sync to local Excel (backup)
    └── Health check: Supabase ✓, Ollama ✓, Excel ✓
    ▼
🌐 Streamlit Dashboard (localhost:8501)
    ├── Reads from Supabase (or Excel)
    ├── Charts, metrics, category breakdown
    ├── AI Insights (Ollama)
    ├── Health monitoring panel
    ├── Error queue viewer
    ├── Manual categorization UI for pending merchants
    └── HTML export
```

**Key insight about laptop dependency:**
- Data is NEVER lost. Supabase stores everything persistently.
- Laptop OFF = processing delayed, not lost. All pending SMS process when laptop comes back.
- Known merchants (90%) can be processed by Supabase Edge Function (FUTURE) without laptop.
- Only unknown merchants (10%) need laptop for Ollama categorization.

---

## Implementation Roadmap (9 Phases)

### ✅ Phase 1: Foundation (COMPLETED)
- config.py, exceptions.py, logger.py, utils.py, validators.py
- Supabase project created, 5 tables, RLS policies, CRUD tested

### Phase 2: Supabase Client (NEXT)
- supabase_client.py with proper error handling
- Migrate CATEGORY_MAP.json → Supabase category_map table
- Migrate existing 480 Excel transactions → Supabase transactions table
- CRUD operations wrapped with retry decorator

### Phase 3: Sync Engine
- sync_engine.py — core pipeline: receive → validate → parse → categorize → save
- 3-level duplicate detection integrated
- Dead letter queue (failed after max retries)
- Concurrency lock

### Phase 4: Listener Service
- listener.py — polls Supabase every 30 sec
- Graceful shutdown (Ctrl+C handler)
- Auto-restart via Windows Task Scheduler
- Health checks (Supabase, Ollama, Excel status)
- Offline SQLite cache when internet down

### Phase 5: Dashboard Upgrades
- Health monitoring panel
- Error queue viewer
- Manual categorization UI for pending merchants
- File uploader (drag-drop JSON import)
- Real-time refresh from Supabase

### Phase 6: Alerting
- Telegram bot for notifications
- Alert on failures, unusual spending
- Daily summary notification

### Phase 7: Testing (pytest)
- test_parser.py, test_categorizer.py, test_validator.py
- test_sync_engine.py, test_duplicates.py
- Mocks for Ollama, Supabase
- Coverage target: >80%

### Phase 8: Phone Setup
- Install SMS Forwarder / MacroDroid on Android
- Configure AXISBK SMS → HTTP POST to Supabase
- End-to-end test with real SMS

### Phase 9: Polish
- CI/CD (GitHub Actions)
- Data retention policy
- Interactive GUI with animations (motion graphics for SMS processing)
- README update

---

## Excel File Details

**Filename:** Ultimate Personal Budget Manager.xlsx
**Location:** D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\

**6 Sheets:**
1. **Settings** — Starting year config
2. **Budget Planning** — Monthly budget allocation per category (Jan-Dec, multi-year)
3. **Budget Tracking** — Raw transaction data (480 records). Columns: C=Date, D=Type, E=Category, F=Amount, G=Merchant|TransactionID. Data starts row 8.
4. **Budget Dashboard** — Category-wise tracked vs budget for selected month. Has Income/Expenses/Savings totals.
5. **Calculations** — Support calculations (today's date, last record, delta, record counts, balance)
6. **Dropdown Data** — Dropdown values for category lists

**DO NOT modify Dashboard, Calculations, Budget Planning sheets programmatically — formulas will break. Only append rows to Budget Tracking.**

---

## Data Insights from Current Transactions

- **480 transactions** from Oct 2025 to May 2026
- **8 months** of data
- **Top expense categories (April 2026):** Food Outside ₹31,685 (37%), Body Care ₹16,172 (19%), Clothing ₹12,533 (15%)
- **Top merchants (April 2026):** Forest Essentials ₹15,467, Zomato ₹12,481 (9 txns), Shanti Ayar ₹10,000 (cleaner salary)
- **Monthly expense range:** ₹41K (Oct) to ₹118K (Jan)
- **Income range:** ₹161K to ₹216K per month

---

## Installed Dependencies

```
pip install openpyxl python-dotenv supabase anthropic requests
pip install streamlit plotly
pip install scikit-learn joblib  # used for ML experiment, can keep
```

**Ollama:** Installed on Windows, version 0.23.1. Model: llama3.1:8b (4.7GB). Server runs on localhost:11434.

---

## Git Info

- **Remote:** https://github.com/vedantpant/sms-budget-tracker.git
- **Branch:** main
- **Latest commit:** Phase 1 foundation (9216259)

---

## Key Things to Remember for Next Session

1. **Vedant wants to WRITE code himself** — don't give complete files, guide step by step with micro-steps
2. **Foundation files were copy-pasted** — he understood them after explanation but hasn't written them himself. He should practice modifying them.
3. **Next: Phase 2** — Build supabase_client.py, migrate data from JSON/Excel to Supabase
4. **validators.py not validator.py** — naming conflict with pip package
5. **Ollama times out on large diffs** in smart_commit.py — may need timeout increase
6. **Excel formulas are a concern** — never modify sheets other than Budget Tracking
7. **.env has real Supabase credentials** — never commit, never share
8. **He wants all edge cases covered** — production-grade, not shortcuts
9. **He wants to learn AI/ML** — the scikit-learn journey was valuable for learning, even though it didn't work for this use case
