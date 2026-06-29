"""
Report Exporter - PDF, CSV, Email functionality
Generates and exports financial reports in multiple formats
"""

import pandas as pd
from datetime import datetime, timedelta
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import plotly.graph_objects as go
import plotly.express as px
from plotly.io import write_html
import base64

from supabase_client import SupabaseClient
from config import Config
from logger import log
from typing import Dict, List, Tuple

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


class ReportExporter:
    """Export financial reports in PDF, CSV, and Email formats"""

    def __init__(self):
        self.supabase = SupabaseClient()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.sender_email = Config.ALERT_EMAIL
        self.sender_password = Config.GMAIL_PASSWORD

    # ==================== DATA LOADING ====================

    def get_transactions(self, period="monthly"):
        """Get transactions for specified period"""
        try:
            all_txns = self.supabase.get_all_transactions()
            df = pd.DataFrame(all_txns) if all_txns else pd.DataFrame()

            if df.empty:
                return df

            df['timestamp'] = pd.to_datetime(df['timestamp'])
            now = datetime.now()

            if period == "daily":
                today = now.date()
                return df[df['timestamp'].dt.date == today]
            elif period == "weekly":
                week_ago = now - timedelta(days=7)
                return df[df['timestamp'] >= week_ago]
            elif period == "monthly":
                return df[
                    (df['timestamp'].dt.year == now.year) &
                    (df['timestamp'].dt.month == now.month)
                ]
            else:
                return df

        except Exception as e:
            log.error(f"Error getting transactions: {e}")
            return pd.DataFrame()

    def calculate_spending(self, df):
        """Calculate spending by category"""
        spending = {}
        for category in BUDGET_CONFIG["categories"].keys():
            amount = df[df['category'] == category]['amount'].sum()
            spending[category] = float(amount) if amount > 0 else 0
        return spending

    # ==================== CSV EXPORT ====================

    def export_to_csv(self, period="monthly", filepath=None):
        """Export transactions to CSV"""
        try:
            df = self.get_transactions(period)

            if df.empty:
                return None, "No transactions found"

            # Select relevant columns
            export_df = df[[
                'timestamp', 'merchant_name', 'amount', 'category', 'type'
            ]].copy()

            export_df.columns = ['Date', 'Merchant', 'Amount', 'Category', 'Type']
            export_df = export_df.sort_values('Date', ascending=False)

            # Save to file or return bytes
            if filepath:
                export_df.to_csv(filepath, index=False)
                log.info(f"CSV exported to {filepath}")
                return filepath, "CSV exported successfully"
            else:
                csv_bytes = export_df.to_csv(index=False).encode('utf-8')
                return csv_bytes, "CSV generated successfully"

        except Exception as e:
            log.error(f"CSV export error: {e}")
            return None, f"Error: {str(e)}"

    # ==================== PDF EXPORT ====================

    def export_to_pdf_html(self, period="monthly"):
        """Generate HTML report (can be converted to PDF)"""
        try:
            df = self.get_transactions(period)

            if df.empty:
                return None, "No transactions found"

            spending = self.calculate_spending(df)

            # Generate HTML content
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Financial Report - {period.capitalize()}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background-color: #f5f5f5;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                    }}
                    .metrics {{
                        display: grid;
                        grid-template-columns: repeat(4, 1fr);
                        gap: 15px;
                        margin-bottom: 20px;
                    }}
                    .metric-card {{
                        background: white;
                        padding: 15px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .metric-label {{
                        font-size: 12px;
                        color: #666;
                        margin-bottom: 5px;
                    }}
                    .metric-value {{
                        font-size: 20px;
                        font-weight: bold;
                        color: #333;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        background: white;
                        margin-top: 20px;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    th {{
                        background-color: #667eea;
                        color: white;
                        padding: 12px;
                        text-align: left;
                    }}
                    td {{
                        padding: 10px 12px;
                        border-bottom: 1px solid #eee;
                    }}
                    tr:hover {{
                        background-color: #f9f9f9;
                    }}
                    .footer {{
                        margin-top: 30px;
                        text-align: center;
                        color: #666;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Financial Report - {period.capitalize()}</h1>
                    <p>Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>
                </div>

                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-label">Monthly Income</div>
                        <div class="metric-value">₹{BUDGET_CONFIG['monthly_income']:,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Total Spent</div>
                        <div class="metric-value">₹{sum(spending.values()):,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Remaining Budget</div>
                        <div class="metric-value">₹{BUDGET_CONFIG['total_budget'] - sum(spending.values()):,.0f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Savings</div>
                        <div class="metric-value">₹{BUDGET_CONFIG['monthly_income'] - sum(spending.values()):,.0f}</div>
                    </div>
                </div>

                <h2>Category Breakdown</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Budget</th>
                        <th>Spent</th>
                        <th>Remaining</th>
                        <th>Usage %</th>
                    </tr>
            """

            for category, budget in BUDGET_CONFIG["categories"].items():
                spent = spending.get(category, 0)
                remaining = budget - spent
                percentage = (spent / budget * 100) if budget > 0 else 0

                html += f"""
                    <tr>
                        <td><strong>{category}</strong></td>
                        <td>₹{budget:,.0f}</td>
                        <td>₹{spent:,.0f}</td>
                        <td>₹{remaining:,.0f}</td>
                        <td>{percentage:.0f}%</td>
                    </tr>
                """

            html += """
                </table>

                <h2>Recent Transactions</h2>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Merchant</th>
                        <th>Amount</th>
                        <th>Category</th>
                        <th>Type</th>
                    </tr>
            """

            for _, row in df.head(20).iterrows():
                html += f"""
                    <tr>
                        <td>{row['timestamp']}</td>
                        <td>{row['merchant_name']}</td>
                        <td>₹{row['amount']:,.0f}</td>
                        <td>{row['category']}</td>
                        <td>{row['type']}</td>
                    </tr>
                """

            html += """
                </table>

                <div class="footer">
                    <p>This is an auto-generated report from your Financial Dashboard</p>
                    <p>Report generated on {}</p>
                </div>
            </body>
            </html>
            """.format(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))

            return html, "HTML report generated successfully"

        except Exception as e:
            log.error(f"PDF export error: {e}")
            return None, f"Error: {str(e)}"

    # ==================== EMAIL EXPORT ====================

    def send_email_report(self, recipient_email, period="monthly", include_attachment=False):
        """Send report via email"""
        try:
            df = self.get_transactions(period)

            if df.empty:
                return False, "No transactions found to send"

            spending = self.calculate_spending(df)
            total_spent = sum(spending.values())

            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Financial Report - {period.capitalize()} ({datetime.now().strftime('%d-%m-%Y')})"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            # HTML content
            html_content = f"""
            <html>
              <body>
                <h2>Financial Report - {period.capitalize()}</h2>
                <p>Report generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>

                <h3>Summary</h3>
                <table border="1" cellpadding="10">
                    <tr>
                        <td><strong>Monthly Income</strong></td>
                        <td>₹{BUDGET_CONFIG['monthly_income']:,.0f}</td>
                    </tr>
                    <tr>
                        <td><strong>Total Spent</strong></td>
                        <td>₹{total_spent:,.0f}</td>
                    </tr>
                    <tr>
                        <td><strong>Budget Remaining</strong></td>
                        <td>₹{BUDGET_CONFIG['total_budget'] - total_spent:,.0f}</td>
                    </tr>
                    <tr>
                        <td><strong>Current Savings</strong></td>
                        <td>₹{BUDGET_CONFIG['monthly_income'] - total_spent:,.0f}</td>
                    </tr>
                </table>

                <h3>Top Spending Categories</h3>
                <ul>
            """

            sorted_spending = sorted(spending.items(), key=lambda x: x[1], reverse=True)
            for category, amount in sorted_spending[:5]:
                budget = BUDGET_CONFIG["categories"][category]
                percentage = (amount / budget * 100) if budget > 0 else 0
                html_content += f"<li>{category}: ₹{amount:,.0f} ({percentage:.0f}% of budget)</li>"

            html_content += """
                </ul>

                <p>
                    <strong>Best Regards,</strong><br>
                    Your Financial Dashboard
                </p>
              </body>
            </html>
            """

            # Attach HTML
            msg.attach(MIMEText(html_content, 'html'))

            # Attach CSV if requested
            if include_attachment:
                csv_data, _ = self.export_to_csv(period)
                if csv_data:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(csv_data)
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename= "report_{period}_{datetime.now().strftime("%Y%m%d")}.csv"'
                    )
                    msg.attach(attachment)

            # Send email
            try:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                server.quit()

                log.info(f"Email report sent to {recipient_email}")
                return True, f"Report sent to {recipient_email}"

            except smtplib.SMTPAuthenticationError:
                log.error("Gmail authentication failed")
                return False, "Email authentication failed. Check your app password."
            except smtplib.SMTPException as e:
                log.error(f"SMTP error: {e}")
                return False, f"Email send failed: {str(e)}"

        except Exception as e:
            log.error(f"Email report error: {e}")
            return False, f"Error: {str(e)}"

    # ==================== SCHEDULED REPORTS ====================

    def schedule_daily_report(self, recipient_email):
        """Schedule daily report (helper function)"""
        return self.send_email_report(recipient_email, "daily", include_attachment=True)

    def schedule_weekly_report(self, recipient_email):
        """Schedule weekly report (helper function)"""
        return self.send_email_report(recipient_email, "weekly", include_attachment=True)

    def schedule_monthly_report(self, recipient_email):
        """Schedule monthly report (helper function)"""
        return self.send_email_report(recipient_email, "monthly", include_attachment=True)
