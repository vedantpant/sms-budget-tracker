"""
Simple Budget Dashboard
Clean, minimal UI with Budget, Pie Chart, and AI Suggestions
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from supabase_client import SupabaseClient
from logger import log

# Page config
st.set_page_config(
    page_title="Budget Dashboard",
    page_icon="💰",
    layout="wide"
)

# Budget Configuration
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
    }
}

# Initialize
@st.cache_resource
def init_supabase():
    return SupabaseClient()

supabase = init_supabase()

# ==================== DATA LOADING ====================

@st.cache_data(ttl=60)
def load_current_month_data():
    """Load current month transactions"""
    try:
        all_txns = supabase.get_all_transactions()
        df = pd.DataFrame(all_txns) if all_txns else pd.DataFrame()

        if df.empty:
            return df, {}

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        now = datetime.now()
        current_month = df[
            (df['timestamp'].dt.year == now.year) &
            (df['timestamp'].dt.month == now.month)
        ]

        # Calculate spending by category
        spending = {}
        for category in BUDGET_CONFIG["categories"].keys():
            amount = current_month[current_month['category'] == category]['amount'].sum()
            spending[category] = float(amount) if amount > 0 else 0

        return current_month, spending

    except Exception as e:
        log.error(f"Error loading data: {e}")
        return pd.DataFrame(), {}


def get_budget_status(spending):
    """Get simple budget status"""
    status = {}
    for category, budget in BUDGET_CONFIG["categories"].items():
        spent = spending.get(category, 0)
        remaining = budget - spent
        percentage = (spent / budget * 100) if budget > 0 else 0

        status[category] = {
            "budget": budget,
            "spent": spent,
            "remaining": remaining,
            "percentage": percentage
        }

    return status


def get_ai_suggestions(spending):
    """Generate AI suggestions"""
    suggestions = []

    # Over budget alerts
    for category, budget in BUDGET_CONFIG["categories"].items():
        spent = spending.get(category, 0)
        if spent > budget:
            overage = spent - budget
            suggestions.append({
                "type": "alert",
                "text": f"⚠️ {category} exceeded by ₹{overage:,.0f}"
            })

    # Savings opportunity
    total_spent = sum(spending.values())
    if total_spent < BUDGET_CONFIG["total_budget"] * 0.5:
        suggestions.append({
            "type": "good",
            "text": f"✅ Great! You've spent only {(total_spent/BUDGET_CONFIG['total_budget']*100):.0f}% of your budget"
        })

    if not suggestions:
        suggestions.append({
            "type": "info",
            "text": "📊 You're on track with your budget!"
        })

    return suggestions


# ==================== MAIN UI ====================

st.title("💰 Budget Dashboard")

# Load data
df, spending = load_current_month_data()
budget_status = get_budget_status(spending)

# Row 1: Key Metrics
col1, col2, col3, col4 = st.columns(4)

total_spent = sum(spending.values())
remaining = BUDGET_CONFIG["total_budget"] - total_spent
savings = BUDGET_CONFIG["monthly_income"] - total_spent

with col1:
    st.metric("Monthly Income", f"₹{BUDGET_CONFIG['monthly_income']:,.0f}")

with col2:
    st.metric("Budget", f"₹{BUDGET_CONFIG['total_budget']:,.0f}")

with col3:
    st.metric("Spent", f"₹{total_spent:,.0f}", delta=f"{(total_spent/BUDGET_CONFIG['total_budget']*100):.0f}%")

with col4:
    st.metric("Remaining", f"₹{remaining:,.0f}", delta=f"₹{savings:,.0f} savings")

st.markdown("---")

# Row 2: Pie Chart
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Spending by Category")

    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(spending.keys()),
        values=list(spending.values()),
        hole=0.3,
        textposition='inside',
        textinfo='label+percent'
    )])

    fig.update_layout(
        height=400,
        showlegend=True,
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Category Status")

    # Simple category list
    for category in sorted(spending.keys(), key=lambda x: spending[x], reverse=True):
        status = budget_status[category]
        spent = status['spent']
        budget = status['budget']
        percentage = status['percentage']

        # Color code
        if percentage > 100:
            color = "🔴"
        elif percentage > 80:
            color = "🟡"
        else:
            color = "🟢"

        st.write(f"{color} **{category}**")
        st.write(f"  ₹{spent:,.0f} / ₹{budget:,.0f} ({percentage:.0f}%)")

st.markdown("---")

# Row 3: AI Suggestions
st.subheader("🤖 Smart Suggestions")

suggestions = get_ai_suggestions(spending)

for suggestion in suggestions:
    if suggestion['type'] == 'alert':
        st.warning(suggestion['text'])
    elif suggestion['type'] == 'good':
        st.success(suggestion['text'])
    else:
        st.info(suggestion['text'])

st.markdown("---")

# Row 3: Monthly Spending Trend
st.subheader("📅 Monthly Spending Trend")

# Get monthly data
all_txns = supabase.get_all_transactions()
if all_txns:
    df_all = pd.DataFrame(all_txns)
    df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
    df_all['month'] = df_all['timestamp'].dt.to_period('M')

    monthly_spending = df_all.groupby('month')['amount'].sum().reset_index()
    monthly_spending['month'] = monthly_spending['month'].astype(str)

    if not monthly_spending.empty:
        # Create line chart
        fig_monthly = go.Figure()

        fig_monthly.add_trace(go.Scatter(
            x=monthly_spending['month'],
            y=monthly_spending['amount'],
            mode='lines+markers',
            name='Monthly Spending',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))

        # Add budget line
        fig_monthly.add_hline(
            y=BUDGET_CONFIG['total_budget'],
            line_dash="dash",
            line_color="red",
            annotation_text="Budget",
            annotation_position="right"
        )

        fig_monthly.update_layout(
            height=300,
            xaxis_title='Month',
            yaxis_title='Spending (₹)',
            hovermode='x unified',
            showlegend=True
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            st.plotly_chart(fig_monthly, use_container_width=True)

        with col2:
            st.subheader("Monthly Stats")
            st.write(f"**Latest Month:** ₹{monthly_spending['amount'].iloc[-1]:,.0f}")
            if len(monthly_spending) > 1:
                prev_month = monthly_spending['amount'].iloc[-2]
                current_month = monthly_spending['amount'].iloc[-1]
                change = ((current_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
                st.write(f"**Change:** {change:+.0f}%")
            st.write(f"**Average:** ₹{monthly_spending['amount'].mean():,.0f}")

st.markdown("---")

# Row 4: Add Transaction (Simple Form)
st.subheader("➕ Add Transaction")

col1, col2, col3, col4 = st.columns(4)

with col1:
    merchant = st.text_input("Merchant", placeholder="e.g., Zomato")

with col2:
    amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)

with col3:
    category = st.selectbox("Category", list(BUDGET_CONFIG["categories"].keys()))

with col4:
    if st.button("Add", type="primary", use_container_width=True):
        if merchant and amount > 0:
            try:
                import uuid
                result = supabase.insert_transaction({
                    'sms_id': None,
                    'amount': amount,
                    'merchant_name': merchant,
                    'type': 'Expenses',
                    'category': category,
                    'transaction_id': f"MANUAL_{uuid.uuid4().hex[:12].upper()}",
                    'timestamp': f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    'account_number': '0316'
                })

                if result:
                    st.success(f"✅ Added: {merchant} - ₹{amount:,.0f}")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Failed to add transaction")

            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Enter merchant name and amount")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
Simple Budget Dashboard | Real-time tracking from Supabase
</div>
""", unsafe_allow_html=True)
