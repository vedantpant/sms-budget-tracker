# 💰 SMS Budget Tracker - Ultimate Personal Budget Manager

> **Real-time budget tracking with bank reconciliation, AI-powered categorization, and cloud-based dashboard.**

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Active-brightgreen)

---

## 🌟 Overview

A comprehensive budget management system that automatically tracks your spending through SMS notifications, reconciles with bank statements, and provides real-time financial insights through an interactive dashboard.

**Key Highlights:**
- 📱 Auto-sync SMS transactions from your bank
- 🏦 Bank statement reconciliation with duplicate detection
- 🤖 AI-powered smart categorization
- 📊 Real-time interactive budget dashboard
- 💾 Automatic Excel synchronization
- ☁️ Cloud-deployed (Streamlit Cloud)
- 🔒 Secure & encrypted (Supabase)
- 📈 Advanced analytics & trends

---

## ✨ Features

### 📊 Budget Dashboard
- **Real-time Overview:** Income, budget, spending, and remaining amounts
- **Income Analysis:** Compare income vs expenses vs investments vs savings
- **Visual Charts:** Pie charts, line graphs, bar charts for easy understanding
- **Category Tracking:** 8 budget categories with color-coded alerts
- **Monthly Trends:** Spending patterns over time
- **Interactive Filtering:** View any month's breakdown

### 🤖 Smart Features
- **AI Categorization:** Ollama AI automatically categorizes transactions
- **Smart Suggestions:** Budget recommendations and overspending alerts
- **Pattern Detection:** Identifies spending trends and anomalies
- **Auto-sync:** Real-time updates from Supabase

### 🏦 Bank Reconciliation
- **Statement Import:** CSV-based bank statement reconciliation
- **Duplicate Detection:** Prevents duplicate transaction entries
- **Auto-Categorization:** AI categorizes missing transactions
- **Excel Sync:** Automatic synchronization to your Excel tracker
- **Missing Transaction Detection:** Identifies transactions in statement but not in database

### 📱 Transaction Management
- **SMS Forwarder:** Automatic SMS → Supabase sync
- **Manual Entry:** Quick form to add transactions
- **Bulk Import:** One-time import from exported SMS
- **Error Recovery:** Automatic retry with exponential backoff

### 📈 Analytics & Reports
- **Daily/Weekly/Monthly Reports:** Automated email summaries
- **Export Options:** PDF, CSV, HTML formats
- **Email Integration:** Scheduled reports via Gmail
- **Detailed Breakdowns:** Category-wise spending analysis
- **Trend Analysis:** Compare months and identify patterns

### 🔐 Security
- **Encrypted Secrets:** All credentials in Streamlit Cloud Secrets
- **Database Security:** Supabase PostgreSQL with RLS
- **Secure API:** REST API with authentication
- **No Hardcoded Credentials:** Best security practices

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account (free tier works)
- Gmail account with app password
- GitHub account (optional, for cloud deployment)
- Streamlit Cloud account (for dashboard)

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/vedantpant/sms-budget-tracker.git
cd sms-budget-tracker/app_tracker

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 5. Run dashboard locally
streamlit run simple_budget_dashboard.py
```

**Dashboard opens at:** `http://localhost:8501`

---

## ☁️ Cloud Deployment

### Deploy on Streamlit Cloud (Free!)

1. **Push to GitHub** (already done ✓)
2. **Go to:** https://streamlit.io/cloud
3. **Create New App:**
   - Repository: `vedantpant/sms-budget-tracker`
   - Branch: `main`
   - File: `simple_budget_dashboard.py`
4. **Add Secrets:** Settings → Secrets
5. **Deploy** ✅

---

## 📋 Project Structure

```
app_tracker/
├── simple_budget_dashboard.py      # Main dashboard
├── bank_reconciliation_csv.py      # CSV reconciliation
├── excel_sync.py                   # Excel sync
├── report_exporter.py              # Export features
├── supabase_client.py              # Database client
├── sync_engine.py                  # Transaction processing
├── parser.py                       # SMS parsing
├── requirements.txt                # Dependencies
├── README.md                       # This file
├── DASHBOARD_GUIDE.md              # User guide
└── README_DEPLOYMENT.md            # Deployment guide
```

---

## 💾 Technology Stack

### Frontend
- **Streamlit** - Interactive web dashboard
- **Plotly** - Advanced charts & visualizations
- **Pandas** - Data analysis

### Backend
- **Python 3.8+** - Core language
- **Supabase** - PostgreSQL database
- **SQLAlchemy** - Database ORM

### AI/ML
- **Ollama** - Local LLM (llama3.1:8b)

### Deployment
- **Streamlit Cloud** - Dashboard hosting
- **GitHub** - Version control
- **Supabase** - Database & API

---

## 📊 Budget Configuration

Default monthly budget:
```
Monthly Income: ₹1,54,000
Total Budget:   ₹1,00,000

Categories:
- Food Outside:    ₹15,000
- Groceries:       ₹15,000
- Housing:         ₹26,000
- Transportation:  ₹3,000
- Shopping:        ₹10,000
- Entertainment:   ₹3,000
- Stock Portfolio: ₹20,000
- Other:           ₹15,000
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
ALERT_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-16-char-app-password
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
EXCEL_FILE=Ultimate Personal Budget Manager.xlsx
```

---

## 📱 How It Works

### 1. SMS Collection
```
Bank SMS → SMS Forwarder → Supabase → Status: 'new'
```

### 2. Processing
```
listener.py → parse_sms() → categorize() → insert_transaction() → Status: 'processed'
```

### 3. Dashboard
```
Supabase transactions → Real-time sync → Dashboard calculations → Visual charts
```

---

## 📚 Documentation

- **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - Complete user guide
- **[README_DEPLOYMENT.md](README_DEPLOYMENT.md)** - Deployment instructions
- **[CLAUDE.md](CLAUDE.md)** - Technical architecture

---

## 🔐 Security

### Best Practices
- ✅ No credentials in code
- ✅ Environment variables for secrets
- ✅ Streamlit Cloud Secrets for cloud
- ✅ Encrypted database connection
- ✅ HTTPS for all communications
- ✅ Row-level security in Supabase

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push and open a Pull Request

---

## 📞 Support

For help:
1. Check [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)
2. Check [README_DEPLOYMENT.md](README_DEPLOYMENT.md)
3. Review [CLAUDE.md](CLAUDE.md)
4. Open a GitHub issue

---

## 📜 License

MIT License - see LICENSE file for details

---

## 👤 Author

**Vedant Pant**
- GitHub: [@vedantpant](https://github.com/vedantpant)
- Email: vedantpant@gmail.com

---

## ⭐ Show Your Support

If you found this helpful:
- ⭐ Star this repository
- 🔄 Share with others
- 💬 Provide feedback
- 🤝 Contribute improvements

---

**Built with ❤️ for better financial management.**

*Last Updated: June 29, 2026*
