"""
Bank Reconciliation Dashboard
Streamlit UI for bank statement reconciliation with Supabase & Excel sync
"""

import streamlit as st
import pandas as pd
from io import StringIO
import json
from datetime import datetime

from bank_reconciliation_csv import CSVBankReconciliation
from excel_sync import ExcelSync
from logger import log

# Page configuration
st.set_page_config(
    page_title="Bank Reconciliation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .success-text {
        color: #06b6d4;
        font-weight: bold;
    }
    .warning-text {
        color: #f59e0b;
        font-weight: bold;
    }
    .error-text {
        color: #ef4444;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'reconciliation_done' not in st.session_state:
    st.session_state.reconciliation_done = False
if 'reconciliation_result' not in st.session_state:
    st.session_state.reconciliation_result = None
if 'uploaded_df' not in st.session_state:
    st.session_state.uploaded_df = None

# Sidebar
with st.sidebar:
    st.title("Settings")
    st.markdown("---")

    mode = st.radio(
        "Select Mode:",
        ["Reconciliation", "Sync to Excel", "Dashboard"],
        help="Choose what you want to do"
    )

    st.markdown("---")
    st.info("""
    **How it works:**
    1. Upload your bank statement CSV
    2. Preview the data
    3. Run reconciliation
    4. Review results
    5. Sync to Excel
    """)

# Main content
st.title("🏦 Bank Reconciliation Dashboard")
st.markdown("Reconcile your bank statements with automatic duplicate detection")

if mode == "Reconciliation":
    # Reconciliation Mode
    st.header("Step 1: Upload Bank Statement")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type="csv",
        help="Upload your bank statement in CSV format (Date, Transaction Details, Withdrawal, Deposits)"
    )

    if uploaded_file:
        st.success("File uploaded successfully!")

        # Read and display preview
        df = pd.read_csv(uploaded_file)
        st.session_state.uploaded_df = df

        st.header("Step 2: Preview Data")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", len(df))
        col2.metric("Columns", len(df.columns))
        col3.metric("Date Range", f"{df['Date'].min()} to {df['Date'].max()}")

        st.subheader("Data Preview (First 10 rows)")
        st.dataframe(df.head(10), use_container_width=True)

        # Statistics
        st.subheader("Transaction Summary")
        col1, col2, col3 = st.columns(3)

        withdrawals = df['Withdrawal'].fillna(0).sum()
        deposits = df['Deposits'].fillna(0).sum()
        net = deposits - withdrawals

        col1.metric("Total Withdrawals", f"INR {withdrawals:,.2f}")
        col2.metric("Total Deposits", f"INR {deposits:,.2f}")
        col3.metric("Net", f"INR {net:,.2f}")

        st.markdown("---")

        # Run reconciliation
        st.header("Step 3: Run Reconciliation")

        if st.button("Start Reconciliation", key="reconcile_btn", type="primary"):
            with st.spinner("Reconciling transactions..."):
                try:
                    # Save uploaded file temporarily
                    temp_file = "temp_upload.csv"
                    df.to_csv(temp_file, index=False)

                    # Run reconciliation
                    reconciler = CSVBankReconciliation()
                    result = reconciler.reconcile_csv(temp_file)

                    st.session_state.reconciliation_done = True
                    st.session_state.reconciliation_result = result

                    if result.get("status") == "success":
                        st.success("Reconciliation completed successfully!")
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    st.error(f"Error during reconciliation: {str(e)}")
                    log.error(f"[Dashboard] Reconciliation error: {e}")

elif mode == "Sync to Excel":
    # Excel Sync Mode
    st.header("📑 Sync Missing Transactions to Excel")

    st.markdown("""
    This will:
    1. Find transactions in Supabase but not in Excel
    2. Check for duplicates
    3. Add missing transactions to Excel
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check Sync Status", type="secondary"):
            with st.spinner("Checking status..."):
                try:
                    syncer = ExcelSync()
                    excel_txns = syncer.get_excel_transactions()
                    from supabase_client import SupabaseClient
                    client = SupabaseClient()
                    supabase_txns = client.get_all_transactions()

                    st.info(f"""
                    **Current Status:**
                    - Supabase transactions: {len(supabase_txns)}
                    - Excel transactions: {len(excel_txns)}
                    - Missing in Excel: {len(supabase_txns) - len(excel_txns)}
                    """)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with col2:
        if st.button("Sync Now", type="primary"):
            with st.spinner("Syncing to Excel..."):
                try:
                    syncer = ExcelSync()
                    result = syncer.full_sync()

                    if result.get("status") == "success":
                        st.success(f"Sync Complete! Added {result.get('added_count', 0)} transactions")

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Missing Found", result.get('missing_count', 0))
                        col2.metric("Successfully Added", result.get('added_count', 0))
                        col3.metric("Failed", result.get('failed_count', 0))
                    else:
                        st.info("Excel is already up-to-date!")

                except Exception as e:
                    st.error(f"Error during sync: {str(e)}")
                    log.error(f"[Dashboard] Sync error: {e}")

else:
    # Dashboard Mode
    st.header("📊 Reconciliation Dashboard")

    if st.session_state.reconciliation_done and st.session_state.reconciliation_result:
        result = st.session_state.reconciliation_result

        # Results Summary
        st.subheader("Reconciliation Results")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Bank Transactions", result.get('total_bank_txns', 0))
        col2.metric("Supabase Transactions", result.get('total_supabase_txns', 0))
        col3.metric("Matched", result.get('matched', 0))
        col4.metric("Missing (Added)", result.get('added', 0))

        st.markdown("---")

        # Detailed Report
        st.subheader("Detailed Report")
        report_text = result.get('report', 'No report available')
        st.text(report_text)

        st.markdown("---")

        # Missing Transactions Table
        if result.get('missing_details'):
            st.subheader("Missing Transactions Details (First 20)")

            missing_df = pd.DataFrame(result.get('missing_details', []))
            if not missing_df.empty:
                missing_df = missing_df[[
                    'date', 'merchant_name', 'amount', 'type'
                ]].rename(columns={
                    'date': 'Date',
                    'merchant_name': 'Merchant',
                    'amount': 'Amount',
                    'type': 'Type'
                })

                st.dataframe(missing_df, use_container_width=True)

        # Sync to Excel button
        st.markdown("---")
        st.subheader("Final Step: Sync to Excel")

        if st.button("Sync All to Excel", type="primary", key="sync_final"):
            with st.spinner("Syncing to Excel..."):
                try:
                    syncer = ExcelSync()
                    sync_result = syncer.full_sync()

                    if sync_result.get("status") == "success":
                        st.success(f"Excel Synced! Added {sync_result.get('added_count', 0)} transactions")

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Missing", sync_result.get('missing_count', 0))
                        col2.metric("Successfully Added", sync_result.get('added_count', 0))
                        col3.metric("Failed", sync_result.get('failed_count', 0))
                    else:
                        st.info("No new transactions to sync")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    else:
        st.info("👈 Go to 'Reconciliation' mode to upload and reconcile a bank statement")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p style='color: gray; font-size: 12px;'>
    Bank Reconciliation Dashboard | Phase 8.5 | Built with Streamlit & Supabase
    </p>
</div>
""", unsafe_allow_html=True)
