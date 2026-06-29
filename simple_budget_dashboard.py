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

# Calculate Income, Expenses, Investments, Savings
def calculate_income_expenses_breakdown(df):
    """Calculate income, expenses, investments, and savings"""
    if df.empty:
        return {"income": 0, "expenses": 0, "investments": 0, "savings": 0}

    # Income (credits)
    income = df[df['type'].isin(['Income', 'credit'])]['amount'].sum()

    # Expenses (debits)
    expenses = df[df['type'].isin(['Expenses', 'debit'])]['amount'].sum()

    # Investments (Stock Portfolio category)
    investments = df[df['category'] == 'Stock Portfolio']['amount'].sum()

    # Savings = Income - Expenses - Investments
    savings = income - expenses - investments

    return {
        "income": float(income) if income > 0 else 0,
        "expenses": float(expenses) if expenses > 0 else 0,
        "investments": float(investments) if investments > 0 else 0,
        "savings": float(savings) if savings > 0 else 0
    }

breakdown = calculate_income_expenses_breakdown(df)

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

# Row 1.5: Income vs Expenses vs Investments vs Savings
st.subheader("💰 Income Analysis - Current Month")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "💵 Income",
        f"₹{breakdown['income']:,.0f}",
        delta="Credited",
        delta_color="off"
    )

with col2:
    st.metric(
        "💸 Expenses",
        f"₹{breakdown['expenses']:,.0f}",
        delta=f"{(breakdown['expenses']/breakdown['income']*100):.0f}% of income",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "📈 Investments",
        f"₹{breakdown['investments']:,.0f}",
        delta=f"{(breakdown['investments']/breakdown['income']*100):.0f}% of income",
        delta_color="off"
    )

with col4:
    st.metric(
        "🏦 Savings",
        f"₹{breakdown['savings']:,.0f}",
        delta=f"{(breakdown['savings']/breakdown['income']*100):.0f}% of income",
        delta_color="normal"
    )

with col5:
    savings_rate = (breakdown['savings'] / breakdown['income'] * 100) if breakdown['income'] > 0 else 0
    st.metric(
        "📊 Savings Rate",
        f"{savings_rate:.0f}%",
        delta="Target: 35%",
        delta_color="off"
    )

# Comparison Chart
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Income Distribution")

    # Waterfall chart showing flow
    fig_waterfall = go.Figure(go.Waterfall(
        x=['Income', 'Expenses', 'Investments', 'Savings'],
        y=[breakdown['income'], -breakdown['expenses'], -breakdown['investments'], breakdown['savings']],
        marker=dict(color=['green', 'red', 'orange', 'blue']),
        connector=dict(line=dict(color='gray'))
    ))

    fig_waterfall.update_layout(
        height=300,
        showlegend=False,
        xaxis_title='Category',
        yaxis_title='Amount (₹)'
    )

    st.plotly_chart(fig_waterfall, use_container_width=True)

with col2:
    st.subheader("📈 Breakdown Table")

    breakdown_data = {
        "Category": ["Income", "Expenses", "Investments", "Savings"],
        "Amount": [
            f"₹{breakdown['income']:,.0f}",
            f"₹{breakdown['expenses']:,.0f}",
            f"₹{breakdown['investments']:,.0f}",
            f"₹{breakdown['savings']:,.0f}"
        ],
        "% of Income": [
            "100%",
            f"{(breakdown['expenses']/breakdown['income']*100):.0f}%",
            f"{(breakdown['investments']/breakdown['income']*100):.0f}%",
            f"{(breakdown['savings']/breakdown['income']*100):.0f}%"
        ]
    }

    breakdown_df = pd.DataFrame(breakdown_data)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

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

# Row 4.5: Month Selector
st.subheader("🗓️ Select Month to View Breakdown")

all_txns_for_months = supabase.get_all_transactions()
if all_txns_for_months:
    df_for_months = pd.DataFrame(all_txns_for_months)
    df_for_months['timestamp'] = pd.to_datetime(df_for_months['timestamp'])
    df_for_months['month'] = df_for_months['timestamp'].dt.to_period('M').astype(str)

    # Get available months
    available_months = sorted(df_for_months['month'].unique(), reverse=True)

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        selected_month = st.selectbox(
            "Choose Month:",
            available_months,
            index=0,
            help="Select a month to see detailed category breakdown"
        )

    # Get data for selected month
    selected_month_data = df_for_months[df_for_months['month'] == selected_month]

    if not selected_month_data.empty:
        selected_spending = {}
        for category in BUDGET_CONFIG["categories"].keys():
            amount = selected_month_data[selected_month_data['category'] == category]['amount'].sum()
            selected_spending[category] = float(amount) if amount > 0 else 0

        selected_total = sum(selected_spending.values())

        with col2:
            st.metric("Total Spent", f"₹{selected_total:,.0f}")

        with col3:
            remaining = BUDGET_CONFIG["total_budget"] - selected_total
            st.metric("Budget Left", f"₹{remaining:,.0f}")

        st.markdown("---")

        # Show breakdown for selected month
        st.subheader(f"📊 Breakdown for {selected_month}")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Pie chart for selected month
            fig_month_pie = go.Figure(data=[go.Pie(
                labels=list(selected_spending.keys()),
                values=list(selected_spending.values()),
                hole=0.3,
                textposition='inside',
                textinfo='label+percent'
            )])

            fig_month_pie.update_layout(
                height=400,
                showlegend=True
            )

            st.plotly_chart(fig_month_pie, use_container_width=True)

        with col2:
            st.subheader("Category Details")

            # Sort by spending
            sorted_categories = sorted(selected_spending.items(), key=lambda x: x[1], reverse=True)

            for category, spent in sorted_categories:
                budget = BUDGET_CONFIG["categories"][category]
                remaining_cat = budget - spent
                pct = (spent / budget * 100) if budget > 0 else 0

                # Color code
                if pct > 100:
                    color = "🔴"
                    status = "Over"
                elif pct > 80:
                    color = "🟡"
                    status = "Warning"
                else:
                    color = "🟢"
                    status = "OK"

                st.write(f"{color} **{category}**")
                st.write(f"  ₹{spent:,.0f} / ₹{budget:,.0f}")
                st.write(f"  {pct:.0f}% {status}")
                st.write("")

st.markdown("---")

# Row 5: Month-wise Category Breakdown
st.subheader("📈 Month-wise Category Breakdown")

all_txns = supabase.get_all_transactions()
if all_txns:
    df_all = pd.DataFrame(all_txns)
    df_all['timestamp'] = pd.to_datetime(df_all['timestamp'])
    df_all['month'] = df_all['timestamp'].dt.to_period('M').astype(str)

    # Create pivot table: months vs categories
    pivot_data = df_all.pivot_table(
        values='amount',
        index='month',
        columns='category',
        aggfunc='sum',
        fill_value=0
    )

    if not pivot_data.empty:
        # Stacked bar chart
        fig_category = go.Figure()

        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140']

        for idx, category in enumerate(pivot_data.columns):
            fig_category.add_trace(go.Bar(
                x=pivot_data.index,
                y=pivot_data[category],
                name=category,
                marker_color=colors[idx % len(colors)]
            ))

        fig_category.update_layout(
            barmode='stack',
            height=400,
            xaxis_title='Month',
            yaxis_title='Spending (₹)',
            hovermode='x unified',
            legend=dict(orientation='v', yanchor='top', y=0.99, xanchor='left', x=1.01)
        )

        st.plotly_chart(fig_category, use_container_width=True)

        # Table view
        st.subheader("💾 Category Breakdown Table")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Spending by Category per Month:**")
            st.dataframe(
                pivot_data.style.format('₹{:,.0f}'),
                use_container_width=True
            )

        with col2:
            st.write("**Top Categories Overall:**")
            category_totals = df_all.groupby('category')['amount'].sum().sort_values(ascending=False)
            for idx, (cat, amount) in enumerate(category_totals.head(8).items(), 1):
                budget = BUDGET_CONFIG["categories"].get(cat, 0)
                pct = (amount / budget * 100) if budget > 0 else 0
                st.write(f"{idx}. **{cat}**: ₹{amount:,.0f} ({pct:.0f}% of budget)")

st.markdown("---")

# Row 6: AI Suggestions
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
