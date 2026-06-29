# 💰 Budget Dashboard - Streamlit Cloud Deployment

## Quick Start

### Deploy on Streamlit Cloud (Free!)

1. **Go to Streamlit Cloud:**
   - Visit: https://streamlit.io/cloud
   - Sign in with GitHub

2. **Create New App:**
   - Click "New App"
   - Select repository: `vedantpant/sms-budget-tracker`
   - Select branch: `main`
   - Select file: `simple_budget_dashboard.py`

3. **Add Secrets:**
   - Click "Deploy" 
   - Go to Settings → Secrets
   - Add your environment variables:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ALERT_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
EXCEL_FILE=Ultimate Personal Budget Manager.xlsx
```

4. **Done!** 
   - Your app will be live at: `https://your-app-name.streamlit.app`

---

## Features

✅ **Budget Overview** - Income, Budget, Spent, Remaining  
✅ **Income Analysis** - Compare Income vs Expenses vs Investments vs Savings  
✅ **Pie Chart** - Category distribution  
✅ **Category Status** - Color-coded budget alerts  
✅ **Monthly Trend** - Spending over time  
✅ **Month-wise Breakdown** - Category spending by month  
✅ **Month Selector** - Filter and view specific months  
✅ **AI Suggestions** - Smart budget recommendations  
✅ **Add Transactions** - Quick manual entry  

---

## Budget Configuration

**Monthly Budget:** ₹1,00,000  
**Monthly Income:** ₹1,54,000  

**Categories:**
- Food Outside: ₹15,000
- Groceries: ₹15,000
- Housing: ₹26,000
- Transportation: ₹3,000
- Shopping: ₹10,000
- Entertainment: ₹3,000
- Stock Portfolio: ₹20,000
- Other: ₹15,000

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run dashboard
streamlit run simple_budget_dashboard.py
```

---

## Tech Stack

- **Frontend:** Streamlit
- **Database:** Supabase (PostgreSQL)
- **Charts:** Plotly
- **Data:** Pandas
- **AI:** Ollama (optional)
- **Deployment:** Streamlit Cloud

---

## Important Notes

1. **Ollama AI:** Optional - for advanced categorization
   - Set `OLLAMA_URL` if running locally
   - Dashboard works without it (uses category map)

2. **Excel File:** Required for Excel sync features
   - Not needed for cloud deployment (web-only)

3. **Secrets:** Keep your `.env` file out of GitHub
   - Use Streamlit Cloud Secrets management
   - Never commit `.env` to repo

4. **Database:** All data stored in Supabase
   - Cloud dashboard accesses live data
   - Real-time updates from SMS processing

---

## Support

For issues:
1. Check `.streamlit/config.toml` settings
2. Verify Supabase credentials in Secrets
3. Check Streamlit logs in cloud dashboard
4. Test locally first: `streamlit run simple_budget_dashboard.py`

---

**Happy Budgeting! 🎉**
