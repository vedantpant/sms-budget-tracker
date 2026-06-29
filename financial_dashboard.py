"""
Comprehensive Financial Dashboard
Real-time budget tracking, investments, AI suggestions, and reports
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import defaultdict

from supabase_client import SupabaseClient
from sync_engine import SyncEngine
from logger import log

# Page configuration
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# User's Budget Configuration
BUDGET_CONFIG = {
    "monthly_income": 154000,
    "total_budget": 100000,
    "categories": {
        "Food Outside": 15000,
        "Groceries": 15000,
        "Housing": 26000,
        "Transportation": 3000,
        "Shopping": 10000,
        "Entertainment": 3000,
        "Stock Portfolio": 20000,
        "Other": 15000
    },
    "report_times": {
        "daily": "09:00",
        "weekly": "18:00",
        "monthly": "18:00"
    }
}

# Initialize session state
if 'manual_txn_submitted' not in st.session_state:
    st.session_state.manual_txn_submitted = False

# Initialize clients
@st.cache_resource
def init_clients():
    return {
        "supabase": SupabaseClient(),
        "sync_engine": SyncEngine()
    }

clients = init_clients()
supabase = clients["supabase"]
sync_engine = clients["sync_engine"]

# ==================== DATA LOADING ====================

@st.cache_data(ttl=60)
def load_transactions():
    """Load all transactions from Supabase"""
    try:
        txns = supabase.get_all_transactions()
        return pd.DataFrame(txns) if txns else pd.DataFrame()
    except Exception as e:
        log.error(f"Error loading transactions: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_current_month_transactions():
    """Load current month transactions"""
    try:
        all_txns = supabase.get_all_transactions()
        df = pd.DataFrame(all_txns) if all_txns else pd.DataFrame()

        if df.empty:
            return df

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        now = datetime.now()
        current_month = df[
            (df['timestamp'].dt.year == now.year) &
            (df['timestamp'].dt.month == now.month)
        ]
        return current_month
    except Exception as e:
        log.error(f"Error loading current month transactions: {e}")
        return pd.DataFrame()

# ==================== CALCULATIONS ====================

def calculate_category_spending(df):
    """Calculate spending by category for current month"""
    if df.empty:
        return {}

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    now = datetime.now()
    current_month = df[
        (df['timestamp'].dt.year == now.year) &
        (df['timestamp'].dt.month == now.month)
    ]

    spending = {}
    for category in BUDGET_CONFIG["categories"].keys():
        amount = current_month[current_month['category'] == category]['amount'].sum()
        spending[category] = float(amount) if amount > 0 else 0

    return spending

def calculate_savings_rate(df):
    """Calculate current savings rate"""
    if df.empty:
        return 0

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    now = datetime.now()
    current_month = df[
        (df['timestamp'].dt.year == now.year) &
        (df['timestamp'].dt.month == now.month)
    ]

    total_spent = current_month['amount'].sum()
    remaining = BUDGET_CONFIG["monthly_income"] - total_spent
    savings_rate = (remaining / BUDGET_CONFIG["monthly_income"]) * 100
    return max(0, savings_rate)

def get_budget_status(spending):
    """Get budget status for each category"""
    status = {}
    for category, budget in BUDGET_CONFIG["categories"].items():
        spent = spending.get(category, 0)
        remaining = budget - spent
        percentage = (spent / budget * 100) if budget > 0 else 0

        status[category] = {
            "budget": budget,
            "spent": spent,
            "remaining": remaining,
            "percentage": percentage,
            "status": "🔴 Over" if remaining < 0 else "🟡 Warning" if percentage > 80 else "🟢 OK"
        }

    return status

def get_ai_suggestions(df, spending):
    """Generate AI suggestions based on spending patterns"""
    suggestions = []

    # Overspending alerts
    for category, budget in BUDGET_CONFIG["categories"].items():
        spent = spending.get(category, 0)
        if spent > budget:
            overage = spent - budget
            suggestions.append({
                "type": "warning",
                "category": category,
                "message": f"⚠️ {category} is over budget by ₹{overage:,.0f}"
            })

    # Savings opportunity
    budget_status = get_budget_status(spending)
    underspending = []
    for category, status in budget_status.items():
        if status['remaining'] > status['budget'] * 0.3:  # More than 30% under budget
            underspending.append((category, status['remaining']))

    if underspending:
        total_under = sum([u[1] for u in underspending])
        categories_list = ", ".join([u[0] for u in underspending[:3]])
        suggestions.append({
            "type": "opportunity",
            "message": f"💡 You have ₹{total_under:,.0f} in savings potential across {categories_list}"
        })

    # Investment suggestion
    if spending.get("Stock Portfolio", 0) < BUDGET_CONFIG["categories"]["Stock Portfolio"] * 0.5:
        suggestions.append({
            "type": "investment",
            "message": "📈 Consider increasing your investment allocations for long-term growth"
        })

    # Spending cut suggestion
    total_spent = sum(spending.values())
    if total_spent > BUDGET_CONFIG["total_budget"] * 0.9:
        suggestions.append({
            "type": "optimization",
            "message": f"📉 You're at {(total_spent/BUDGET_CONFIG['total_budget']*100):.0f}% of your budget. Consider reducing discretionary spending"
        })

    return suggestions

# ==================== UI SECTIONS ====================

def show_overview():
    """Show financial overview"""
    st.header("💼 Financial Overview")

    df = load_transactions()
    spending = calculate_category_spending(df)

    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Monthly Income",
            f"₹{BUDGET_CONFIG['monthly_income']:,.0f}",
            delta=None
        )

    with col2:
        total_spent = sum(spending.values())
        st.metric(
            "Total Spent",
            f"₹{total_spent:,.0f}",
            delta=f"{(total_spent/BUDGET_CONFIG['total_budget']*100):.0f}% of budget"
        )

    with col3:
        remaining = BUDGET_CONFIG['total_budget'] - sum(spending.values())
        st.metric(
            "Budget Remaining",
            f"₹{remaining:,.0f}",
            delta="Available"
        )

    with col4:
        savings = BUDGET_CONFIG['monthly_income'] - sum(spending.values())
        st.metric(
            "Current Savings",
            f"₹{savings:,.0f}",
            delta=f"{(savings/BUDGET_CONFIG['monthly_income']*100):.0f}% rate"
        )

    with col5:
        st.metric(
            "Savings Goal",
            f"₹54,000",
            delta=f"Target: 35%"
        )

    st.markdown("---")

def show_budget_tracking():
    """Show budget vs actual spending"""
    st.header("📊 Budget Tracking")

    df = load_transactions()
    spending = calculate_category_spending(df)
    budget_status = get_budget_status(spending)

    # Create budget comparison chart
    categories = list(BUDGET_CONFIG["categories"].keys())
    budget_amounts = [BUDGET_CONFIG["categories"][cat] for cat in categories]
    spent_amounts = [spending.get(cat, 0) for cat in categories]

    fig = go.Figure(data=[
        go.Bar(name='Budget', x=categories, y=budget_amounts, marker_color='lightblue'),
        go.Bar(name='Spent', x=categories, y=spent_amounts, marker_color='salmon')
    ])

    fig.update_layout(
        barmode='group',
        title='Budget vs Actual Spending',
        xaxis_title='Category',
        yaxis_title='Amount (₹)',
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Budget status table
    st.subheader("Category Status")
    status_data = []
    for category, status in budget_status.items():
        status_data.append({
            "Category": category,
            "Budget": f"₹{status['budget']:,.0f}",
            "Spent": f"₹{status['spent']:,.0f}",
            "Remaining": f"₹{status['remaining']:,.0f}",
            "Usage": f"{status['percentage']:.0f}%",
            "Status": status['status']
        })

    status_df = pd.DataFrame(status_data)
    st.dataframe(status_df, use_container_width=True, hide_index=True)

def show_category_breakdown():
    """Show spending by category"""
    st.header("🏷️ Category Breakdown")

    df = load_transactions()
    spending = calculate_category_spending(df)

    # Pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(spending.keys()),
        values=list(spending.values()),
        hole=0.3
    )])

    fig.update_layout(
        title='Spending Distribution by Category',
        height=500
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Categories")
        sorted_spending = sorted(spending.items(), key=lambda x: x[1], reverse=True)
        for idx, (category, amount) in enumerate(sorted_spending[:5], 1):
            st.write(f"{idx}. **{category}**: ₹{amount:,.0f}")

def show_investments():
    """Show investment tracking"""
    st.header("📈 Investment Tracking")

    df = load_transactions()
    spending = calculate_category_spending(df)

    investment_categories = [
        "Stock Portfolio",
        "Mutual Fund",
        "Savings",
        "Gold/Jewelry"
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Investment Allocation")

        investment_data = []
        for cat in investment_categories:
            amount = spending.get(cat, 0)
            budget = BUDGET_CONFIG["categories"].get(cat, 0)
            investment_data.append({
                "Type": cat,
                "Allocated": f"₹{budget:,.0f}",
                "Invested": f"₹{amount:,.0f}",
                "Progress": f"{(amount/budget*100):.0f}%"
            })

        inv_df = pd.DataFrame(investment_data)
        st.dataframe(inv_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Investment Growth")
        total_invested = sum([spending.get(cat, 0) for cat in investment_categories])
        total_allocated = sum([BUDGET_CONFIG["categories"].get(cat, 0) for cat in investment_categories])

        st.metric("Total Invested", f"₹{total_invested:,.0f}")
        st.metric("Total Allocated", f"₹{total_allocated:,.0f}")
        st.metric("Investment Rate", f"{(total_invested/total_allocated*100):.0f}%")

def show_ai_suggestions():
    """Show AI suggestions"""
    st.header("🤖 AI Suggestions & Insights")

    df = load_transactions()
    spending = calculate_category_spending(df)
    suggestions = get_ai_suggestions(df, spending)

    if suggestions:
        for suggestion in suggestions:
            if suggestion['type'] == 'warning':
                st.warning(suggestion['message'])
            elif suggestion['type'] == 'opportunity':
                st.success(suggestion['message'])
            elif suggestion['type'] == 'investment':
                st.info(suggestion['message'])
            elif suggestion['type'] == 'optimization':
                st.info(suggestion['message'])
    else:
        st.success("✅ You're on track with your budget!")

def show_reports():
    """Show daily/weekly/monthly reports"""
    st.header("📄 Reports")

    report_type = st.radio("Select Report Type:", ["Daily", "Weekly", "Monthly"])

    df = load_current_month_transactions()
    spending = calculate_category_spending(df)

    if report_type == "Daily":
        st.subheader("Today's Spending")
        today = datetime.now().date()

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            today_txns = df[df['timestamp'].dt.date == today]

            if not today_txns.empty:
                st.write(f"**Transactions: {len(today_txns)}**")
                st.dataframe(
                    today_txns[['timestamp', 'merchant_name', 'amount', 'category']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No transactions today")

    elif report_type == "Weekly":
        st.subheader("This Week's Summary")

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            week_ago = datetime.now() - timedelta(days=7)
            week_txns = df[df['timestamp'] >= week_ago]

            col1, col2, col3 = st.columns(3)
            col1.metric("Transactions", len(week_txns))
            col2.metric("Total Spent", f"₹{week_txns['amount'].sum():,.0f}")
            col3.metric("Daily Average", f"₹{week_txns['amount'].sum()/7:,.0f}")

    elif report_type == "Monthly":
        st.subheader("This Month's Summary")

        if not df.empty:
            total_spent = df['amount'].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Transactions", len(df))
            col2.metric("Total Spent", f"₹{total_spent:,.0f}")
            col3.metric("Remaining Budget", f"₹{BUDGET_CONFIG['total_budget'] - total_spent:,.0f}")

def show_manual_entry():
    """Show manual transaction entry form"""
    st.header("➕ Add Manual Transaction")

    with st.form("manual_txn_form"):
        col1, col2 = st.columns(2)

        with col1:
            merchant = st.text_input("Merchant Name", placeholder="e.g., Starbucks")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)

        with col2:
            category = st.selectbox("Category", list(BUDGET_CONFIG["categories"].keys()))
            tx_type = st.selectbox("Type", ["Expenses", "Income", "Savings"])

        date = st.date_input("Date")
        notes = st.text_area("Notes (optional)", placeholder="Any additional notes...")

        submitted = st.form_submit_button("Add Transaction", type="primary")

        if submitted:
            if merchant and amount > 0:
                try:
                    # Prepare transaction data
                    timestamp = f"{date.year}-{date.month:02d}-{date.day:02d} 00:00:00"

                    # Insert to Supabase
                    import uuid
                    result = supabase.insert_transaction({
                        'sms_id': None,
                        'amount': amount,
                        'merchant_name': merchant,
                        'type': tx_type,
                        'category': category,
                        'transaction_id': f"MANUAL_{uuid.uuid4().hex[:12].upper()}",
                        'timestamp': timestamp,
                        'account_number': '0316'
                    })

                    if result:
                        st.success(f"✅ Added: {merchant} - ₹{amount:,.0f}")
                        st.session_state.manual_txn_submitted = True
                        st.cache_data.clear()
                    else:
                        st.error("Failed to add transaction")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please fill in merchant name and amount")

# ==================== MAIN APP ====================

def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("📊 Finance Dashboard")
        st.markdown("---")

        page = st.radio(
            "Navigate",
            [
                "Overview",
                "Budget Tracking",
                "Categories",
                "Investments",
                "AI Insights",
                "Reports",
                "Add Transaction"
            ]
        )

        st.markdown("---")
        st.info("""
        **Budget Configuration:**
        - Income: ₹1,54,000/month
        - Budget: ₹1,00,000/month
        - Savings Goal: ₹54,000

        **Report Schedule:**
        - Daily: 9 AM
        - Weekly: Sunday 6 PM
        - Monthly: 1st 6 PM
        """)

    # Main content
    if page == "Overview":
        show_overview()
    elif page == "Budget Tracking":
        show_budget_tracking()
    elif page == "Categories":
        show_category_breakdown()
    elif page == "Investments":
        show_investments()
    elif page == "AI Insights":
        show_ai_suggestions()
    elif page == "Reports":
        show_reports()
    elif page == "Add Transaction":
        show_manual_entry()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Financial Dashboard | Real-time Budget Tracking & AI Insights
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
