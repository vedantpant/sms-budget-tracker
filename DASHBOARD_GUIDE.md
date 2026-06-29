# 💰 Budget Dashboard - Complete User Guide

> **⚠️ SECURITY NOTE:** Your dashboard URL is private. Keep it confidential and don't share it in public repositories, issues, or documentation. Only share with trusted people.

---

## 📊 DASHBOARD OVERVIEW

Your Budget Dashboard is a real-time financial tracking application that connects to your Supabase database and provides comprehensive spending analysis.

**Access your dashboard:** 
- Check your Streamlit Cloud account for your unique app URL
- Format: `https://your-app-name.streamlit.app`
- **Keep this URL private!**

---

## 🎯 FEATURES & HOW TO USE

### **1. Budget Overview (Top Section)**

**What you see:**
- Monthly Income: ₹1,54,000
- Total Budget: ₹1,00,000
- Amount Spent: Real-time from Supabase
- Budget Remaining: Auto-calculated

**How to use:**
- Check at a glance how much you've spent
- Monitor if you're on track with budget
- See remaining amount for the month

---

### **2. Income Analysis**

**What you see:**
- 💵 Income: Total monthly salary/credits
- 💸 Expenses: Total spending (% of income)
- 📈 Investments: Stock/mutual fund allocation
- 🏦 Savings: Income - Expenses - Investments
- 📊 Savings Rate: % of income saved (Target: 35%)

**Bar Chart:**
- Visual comparison of 4 categories
- Color-coded (Green=Income, Red=Expenses, Orange=Investments, Blue=Savings)

**Table:**
- Shows amounts and percentages
- Easy reference format

**How to use:**
- Track if savings rate is on target (35%)
- See how much is going to investments
- Monitor expense ratio vs income
- Make budget adjustments if needed

---

### **3. Pie Chart (Category Distribution)**

**What you see:**
- All 8 spending categories with percentages
- Visual pie chart with color segments
- Interactive hover shows exact amounts

**Categories tracked:**
- Food Outside (₹15,000)
- Groceries (₹15,000)
- Housing (₹26,000)
- Transportation (₹3,000)
- Shopping (₹10,000)
- Entertainment (₹3,000)
- Stock Portfolio (₹20,000)
- Other (₹15,000)

**How to use:**
- See which categories consume most budget
- Identify areas for spending cuts
- Compare actual vs budgeted percentages
- Plan adjustments

---

### **4. Category Status List (Right Side)**

**What you see:**
- All 8 categories with status indicators
- Color coding:
  - 🟢 Green = Under 80% of budget (OK)
  - 🟡 Yellow = 80-100% of budget (Warning)
  - 🔴 Red = Over 100% of budget (Alert!)

**Information shown:**
- Category name
- Spent amount / Budget amount
- Usage percentage
- Status indicator

**How to use:**
- Quickly identify overspending categories
- Get warnings before exceeding budget
- Focus on red categories first
- Plan to reduce spending in yellow categories

---

### **5. Monthly Spending Trend (Line Chart)**

**What you see:**
- Blue line showing spending trend over months
- Red dashed line = Your budget limit (₹1,00,000)
- Interactive hover shows exact amounts

**How to use:**
- See if spending is increasing or decreasing
- Compare months to identify patterns
- Check if consistently above/below budget
- Plan for future months based on trends

---

### **6. Month-wise Category Breakdown**

**Stacked Bar Chart:**
- Shows all 8 categories per month
- Different color for each category
- Height = total spending that month
- Compare spending patterns across months

**Breakdown Table:**
- Rows = Months
- Columns = All 8 categories
- Shows exact amounts for each category-month combo
- Easily spot trends per category

**Top Categories List:**
- Ranked by total spending
- Shows spent vs budget amounts
- Calculates percentage usage
- Helps identify top expense drivers

**How to use:**
- See which categories are increasing/decreasing
- Identify monthly spending patterns
- Plan quarterly budgets
- Analyze seasonal spending

---

### **7. Month Selector (Interactive Filtering)**

**What to do:**
1. Scroll to "Select Month to View Breakdown" section
2. Click dropdown showing available months
3. Select any month (newest first)
4. Dashboard updates instantly

**What updates:**
- Pie chart for that month
- Category details for that month
- Total spent and remaining amounts
- All metrics recalculate for selected month

**How to use:**
- Compare specific months
- Review past spending patterns
- Investigate high spending months
- See category breakdown for any month

---

### **8. AI Smart Suggestions**

**What you see:**
- Overspending alerts (if any category exceeds budget)
- On-track notifications
- Savings opportunity alerts
- Budget optimization tips

**Examples:**
- ⚠️ "Housing exceeded by ₹5,000"
- ✅ "Great! You've spent only 60% of budget"
- 💡 "You have ₹20,000 in savings potential"
- 📉 "Consider reducing discretionary spending"

**How to use:**
- Read suggestions for budget adjustments
- Get alerted to overspending early
- Identify savings opportunities
- Make informed financial decisions

---

### **9. Add Manual Transaction**

**Located at:** Bottom of dashboard

**Form fields:**
- Merchant Name: Who you paid (e.g., "Starbucks", "Amazon")
- Amount: How much (e.g., 250)
- Category: Select from dropdown (all 8 categories)
- Type: "Expenses" (default for manual entries)

**How to use:**
1. For transactions that didn't generate SMS
2. When SMS was missed but transaction happened
3. Manual budget adjustments
4. Override or add missing transactions

**Steps:**
1. Fill in merchant name
2. Enter amount
3. Select category
4. Click "Add"
5. See success message
6. Dashboard updates instantly

---

## 📱 ACCESSING YOUR DASHBOARD

### **From Any Device:**
- Desktop: Full feature access
- Tablet: Responsive layout, all features
- Mobile: Optimized view, fully functional

### **Access Methods:**
1. **Direct URL:** Bookmark your dashboard URL (keep private!)
2. **Streamlit Cloud:** Visit share.streamlit.io to find your app
3. **Share:** Only share URL with trusted people (don't post publicly)

### **Performance:**
- Real-time data from Supabase
- Auto-refreshes every 60 seconds
- Fast loading on most connections
- Optimized for mobile

---

## 🔄 DATA SOURCES

Your dashboard pulls data from:
1. **Supabase Database** (source of truth)
   - Transactions table (all entries)
   - Real-time updates
   - Auto-sync with SMS processing

2. **Budget Configuration** (hardcoded)
   - Monthly income: ₹1,54,000
   - 8 budget categories with limits
   - Auto-calculated metrics

3. **Category Mapping** (Supabase)
   - Auto-categorization from AI
   - Manual overrides supported

---

## 📊 UNDERSTANDING THE NUMBERS

### **Budget vs Actual:**
```
Budget:          ₹1,00,000 (total monthly limit)
Spent:           ₹62,561 (actual spending)
Remaining:       ₹37,439 (budget left)
Spent %:         62.56% (usage percentage)
```

### **Income Analysis:**
```
Income:          ₹1,54,000 (monthly salary)
Expenses:        ₹62,561 (spending)
Investments:     ₹29,314 (stocks/funds)
Savings:         ₹62,125 (leftover)
Savings Rate:    40% (actual vs 35% target)
```

### **Per Category:**
```
Housing:         ₹26,000 budget → ₹26,000 spent = 100% (at limit)
Food Outside:    ₹15,000 budget → ₹5,000 spent = 33% (under budget)
Stock Portfolio: ₹20,000 budget → ₹29,314 spent = 147% (over budget!)
```

---

## ⚠️ COMMON SCENARIOS

### **"I see RED category - what to do?"**
1. Category is over budget
2. Find it in category list
3. Reduce spending in that category
4. Or increase budget if needed

### **"Savings rate is low - what to do?"**
1. Review top spending categories
2. Cut discretionary spending (Shopping, Entertainment)
3. Increase investments if cash allows
4. Check for unexpected expenses

### **"A transaction is missing - what to do?"**
1. Use "Add Manual Transaction" form
2. Fill in details
3. Click "Add"
4. Dashboard updates automatically

### **"I want to change budget amounts - what to do?"**
1. Modify BUDGET_CONFIG in simple_budget_dashboard.py
2. Push to GitHub
3. Dashboard auto-redeploys (~1 minute)
4. Changes take effect immediately

---

## 🔒 SECURITY & PRIVACY

### **Your Data is Secure:**
- ✅ Encrypted connection (HTTPS)
- ✅ Secrets stored securely in Streamlit Cloud
- ✅ Supabase database is encrypted
- ✅ No sensitive data in code

### **Keep Safe:**
- ❌ Don't share your dashboard URL publicly
- ❌ Don't commit secrets to GitHub
- ❌ Don't share SUPABASE_KEY with anyone
- ❌ Don't post screenshots with amounts

### **URL Safety:**
- Your dashboard URL is unique to you
- Treat it like a password
- Only share with people you trust
- Don't post in issues, PRs, or forums

---

## 🛠️ UPDATING DASHBOARD

### **If you change code locally:**

1. Edit `simple_budget_dashboard.py` locally
2. Test with: `streamlit run simple_budget_dashboard.py`
3. Commit: `git add . && git commit -m "message"`
4. Push: `git push origin main`
5. Dashboard auto-updates (~1 minute)
6. Refresh browser to see changes

### **If you change budget:**

Edit in code:
```python
BUDGET_CONFIG = {
    "monthly_income": 154000,
    "total_budget": 100000,
    "categories": {
        "Food Outside": 15000,  # Change these
        "Groceries": 15000,
        ...
    }
}
```

Then commit and push (same steps as above).

---

## 📞 TROUBLESHOOTING

### **Dashboard shows "No data"**
- Check Supabase connection
- Verify SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets
- Ensure transactions exist in Supabase

### **Charts not updating**
- Refresh browser (F5)
- Wait 60 seconds for cache refresh
- Check if new transactions were added to Supabase

### **Add Transaction not working**
- Fill in all required fields
- Check merchant name not empty
- Check amount > 0
- Try again

### **Numbers seem wrong**
- Check for duplicate transactions in Supabase
- Verify category mappings are correct
- Compare Supabase data with dashboard display

### **Can't access dashboard**
- Check if URL is correct (bookmark it)
- Verify Streamlit Cloud account is active
- Check if app is deployed (should say "Running")
- Try refreshing page

---

## 📈 TIPS FOR BEST RESULTS

1. **Add transactions daily** - Keep data current
2. **Review weekly** - Check trends early
3. **Monitor red alerts** - Address overspending immediately
4. **Plan monthly** - Review month-end summary
5. **Adjust budget** - Based on actual spending patterns
6. **Set goals** - Use AI suggestions for targets

---

## 📚 RELATED DOCUMENTATION

- **Deployment Guide:** README_DEPLOYMENT.md
- **Project Overview:** CLAUDE.md
- **GitHub Repo:** https://github.com/vedantpant/sms-budget-tracker

---

## ✅ QUICK START CHECKLIST

- [ ] Bookmarked dashboard URL (keep private!)
- [ ] Accessed dashboard from browser
- [ ] Saw budget overview with your data
- [ ] Viewed pie chart and categories
- [ ] Selected a different month
- [ ] Added a test transaction
- [ ] Saw dashboard update
- [ ] Reviewed AI suggestions
- [ ] Checked savings rate

---

**Enjoy your Budget Dashboard! 💰**

For technical questions, check CLAUDE.md or the GitHub repo.
