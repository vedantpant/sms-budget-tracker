# SMS Budget Tracker — Production-Grade Implementation Roadmap

## 🎯 Goal
Fully automated, production-grade SMS budget tracking system with cloud sync,
AI categorization, real-time dashboard, and comprehensive error handling.

---

## Phase 1: Foundation (Session 1)
**Files:** `config.py`, `exceptions.py`, `utils.py`, `logger.py`, `validator.py`

- [ ] Configuration management (config.yaml + .env)
- [ ] Custom exception hierarchy (15+ exception classes)
- [ ] Retry decorator with exponential backoff
- [ ] Circuit breaker pattern
- [ ] Logging framework (file + console, rotating logs)
- [ ] Input validation & sanitization
- [ ] Timezone handler (IST ↔ UTC)

---

## Phase 2: Supabase Setup (Session 2)
**Files:** `supabase_client.py`, SQL schema

- [ ] Create Supabase project
- [ ] Create tables: `sms_raw`, `transactions`, `category_map`, `error_log`, `audit_trail`
- [ ] Row Level Security policies
- [ ] Python Supabase client with connection pooling
- [ ] CRUD operations with error handling
- [ ] Migrate existing CATEGORY_MAP.json → Supabase
- [ ] Migrate existing Excel transactions → Supabase
- [ ] Duplicate detection (hash + transaction_id)

---

## Phase 3: Core Sync Engine (Session 3)
**Files:** `sync_engine.py`

- [ ] SMS ingestion pipeline (receive → validate → store)
- [ ] Processing pipeline (parse → categorize → save)
- [ ] 4-layer categorization (exact → fuzzy → Ollama → manual)
- [ ] Dead letter queue (failed after max retries)
- [ ] Graceful partial failure handling
- [ ] Excel sync (Supabase → local Excel backup)
- [ ] Concurrency lock (prevent double processing)
- [ ] Idempotent operations

---

## Phase 4: Listener Service (Session 4)
**Files:** `listener.py`, `health_check.py`

- [ ] Supabase polling listener (30 sec interval)
- [ ] Graceful shutdown (SIGINT/SIGTERM handler)
- [ ] Auto-restart on crash (Task Scheduler config)
- [ ] Health check endpoint (Supabase, Ollama, Excel)
- [ ] Heartbeat logging
- [ ] Offline cache (SQLite fallback when internet down)
- [ ] Online sync (flush cache when internet returns)

---

## Phase 5: Dashboard Upgrades (Session 5)
**Files:** `dashboard.py` updates

- [ ] Health monitoring panel (service statuses)
- [ ] Error queue viewer (pending/failed SMS)
- [ ] Manual categorization UI (for pending merchants)
- [ ] File uploader (drag-drop JSON import)
- [ ] Real-time refresh from Supabase
- [ ] Audit trail viewer
- [ ] Performance metrics (processing times, success rates)
- [ ] HTML export with AI insights

---

## Phase 6: Alerting & Notifications (Session 6)
**Files:** `alerting.py`

- [ ] Telegram bot setup
- [ ] Alert on: 5 consecutive failures
- [ ] Alert on: new transaction processed (optional)
- [ ] Alert on: unusual spending detected
- [ ] Daily summary notification
- [ ] Alert cooldown (don't spam)

---

## Phase 7: Testing Suite (Session 7)
**Files:** `tests/` directory

- [ ] test_parser.py — all 4 regex patterns + edge cases
- [ ] test_categorizer.py — exact, fuzzy, Ollama mock
- [ ] test_validator.py — input sanitization
- [ ] test_sync_engine.py — full pipeline with mocks
- [ ] test_duplicates.py — all 3 duplicate levels
- [ ] test_exceptions.py — error handling flows
- [ ] test_retry.py — retry + circuit breaker
- [ ] conftest.py — fixtures, mocks
- [ ] Coverage report (target: >80%)

---

## Phase 8: Phone Setup (Session 8)

- [ ] Install SMS Forwarder / MacroDroid on phone
- [ ] Configure AXISBK SMS → HTTP POST to Supabase
- [ ] End-to-end test (real SMS → Supabase → process → Excel)
- [ ] Verify duplicate handling (bulk import + sync overlap)

---

## Phase 9: Polish & Deploy (Session 9)

- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Data retention policy (auto-cleanup old raw SMS)
- [ ] Schema migration framework
- [ ] Performance metrics dashboard
- [ ] README.md update (setup guide, architecture diagram)
- [ ] Interactive GUI with animations (bonus)

---

## Architecture Diagram

```
📱 Phone (SMS Forwarder)
    │ HTTP POST
    ▼
☁️ Supabase (PostgreSQL + Real-time)
    ├── sms_raw (raw SMS, deduplicated)
    ├── transactions (processed, categorized)
    ├── category_map (merchant → category)
    ├── error_log (failures + retries)
    └── audit_trail (who changed what)
    │
    ├── Edge Function: auto-categorize known merchants
    │
    ▼
💻 Laptop (auto-start on boot)
    ├── listener.py (polls Supabase every 30s)
    ├── sync_engine.py (parse → categorize → save)
    ├── ai_categorizer.py (Ollama for unknowns)
    ├── health_check.py (monitor all services)
    └── Excel sync (backup)
    │
    ▼
🌐 Streamlit Dashboard (localhost:8501)
    ├── Charts, metrics, category breakdown
    ├── AI Insights (Ollama)
    ├── Health monitoring panel
    ├── Error queue viewer
    ├── Manual categorization UI
    └── HTML export
```

## Tech Stack
- **Language:** Python 3.13
- **Database:** Supabase (PostgreSQL)
- **AI:** Ollama (llama3.1:8b)
- **Dashboard:** Streamlit + Plotly
- **Excel:** openpyxl
- **Testing:** pytest + coverage
- **CI/CD:** GitHub Actions
- **Alerting:** Telegram Bot API
- **Automation:** Windows Task Scheduler
```
