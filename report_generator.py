"""
Report Generator — Daily, Weekly, Monthly Expenditure Reports
Queries Supabase for transactions and generates formatted reports
"""
from supabase_client import SupabaseClient
from datetime import datetime, timedelta
from logger import log

class ReportGenerator:
    def __init__(self):
        self.db = SupabaseClient()

    def get_daily_transactions(self, date=None):
        """Get transactions for a specific day (default: today)"""
        if date is None:
            date = datetime.now().date()

        try:
            # Convert date to ISO format for Supabase query
            start_of_day = datetime.combine(date, datetime.min.time()).isoformat()
            end_of_day = datetime.combine(date, datetime.max.time()).isoformat()

            response = self.db.client.table('transactions') \
                .select('*') \
                .gte('timestamp', start_of_day) \
                .lte('timestamp', end_of_day) \
                .execute()

            return response.data if response.data else []

        except Exception as e:
            log.error(f"Error fetching daily transactions: {e}")
            return []

    def get_weekly_transactions(self, end_date=None):
        """Get transactions for the last 7 days"""
        if end_date is None:
            end_date = datetime.now().date()

        start_date = end_date - timedelta(days=7)

        try:
            start_iso = datetime.combine(start_date, datetime.min.time()).isoformat()
            end_iso = datetime.combine(end_date, datetime.max.time()).isoformat()

            response = self.db.client.table('transactions') \
                .select('*') \
                .gte('timestamp', start_iso) \
                .lte('timestamp', end_iso) \
                .execute()

            return response.data if response.data else []

        except Exception as e:
            log.error(f"Error fetching weekly transactions: {e}")
            return []

    def get_monthly_transactions(self, year=None, month=None):
        """Get transactions for a specific month (default: current month)"""
        if year is None or month is None:
            today = datetime.now()
            year, month = today.year, today.month

        try:
            # First day of the month
            start_date = datetime(year, month, 1)

            # Last day of the month
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)

            start_iso = start_date.isoformat()
            end_iso = datetime.combine(end_date.date(), datetime.max.time()).isoformat()

            response = self.db.client.table('transactions') \
                .select('*') \
                .gte('timestamp', start_iso) \
                .lte('timestamp', end_iso) \
                .execute()

            return response.data if response.data else []

        except Exception as e:
            log.error(f"Error fetching monthly transactions: {e}")
            return []

    def calculate_totals_by_category(self, transactions):
        """Calculate total amount and count by category"""
        category_totals = {}

        for txn in transactions:
            # Only count expenses (not income)
            if txn.get('type') == 'Expenses':
                category = txn.get('category', 'Uncategorized')
                amount = float(txn.get('amount', 0))

                if category not in category_totals:
                    category_totals[category] = {'amount': 0, 'count': 0}

                category_totals[category]['amount'] += amount
                category_totals[category]['count'] += 1

        return category_totals

    def get_top_merchants(self, transactions, limit=5):
        """Get top merchants by spending"""
        merchant_totals = {}

        for txn in transactions:
            if txn.get('type') == 'Expenses':
                merchant = txn.get('merchant_name', 'Unknown')
                amount = float(txn.get('amount', 0))

                if merchant not in merchant_totals:
                    merchant_totals[merchant] = 0

                merchant_totals[merchant] += amount

        # Sort by amount and return top N
        sorted_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)
        return sorted_merchants[:limit]

    def calculate_total_spending(self, transactions):
        """Calculate total spending (expenses only)"""
        total = 0
        for txn in transactions:
            if txn.get('type') == 'Expenses':
                total += float(txn.get('amount', 0))
        return total

    def calculate_total_income(self, transactions):
        """Calculate total income"""
        total = 0
        for txn in transactions:
            if txn.get('type') == 'Income':
                total += float(txn.get('amount', 0))
        return total

    def format_daily_report(self):
        """Generate formatted daily spending report"""
        today = datetime.now().date()
        transactions = self.get_daily_transactions(today)

        if not transactions:
            return {
                "subject": f"Daily Spending Report - {today.strftime('%B %d, %Y')}",
                "total_spent": 0,
                "transaction_count": 0,
                "top_merchants": [],
                "category_breakdown": {},
                "html_body": f"<p>No transactions today ({today.strftime('%B %d, %Y')}).</p>"
            }

        total_spent = self.calculate_total_spending(transactions)
        category_breakdown = self.calculate_totals_by_category(transactions)
        top_merchants = self.get_top_merchants(transactions, limit=5)

        # Generate HTML report
        html_body = self._generate_html_report(
            title="📊 DAILY SPENDING REPORT",
            date=today.strftime('%B %d, %Y'),
            total_spent=total_spent,
            transaction_count=len(transactions),
            top_merchants=top_merchants,
            category_breakdown=category_breakdown
        )

        return {
            "subject": f"Daily Spending Report - {today.strftime('%B %d, %Y')}",
            "total_spent": total_spent,
            "transaction_count": len(transactions),
            "top_merchants": top_merchants,
            "category_breakdown": category_breakdown,
            "html_body": html_body
        }

    def format_weekly_report(self):
        """Generate formatted weekly spending report"""
        today = datetime.now().date()
        start_date = today - timedelta(days=7)
        transactions = self.get_weekly_transactions(today)

        if not transactions:
            return {
                "subject": f"Weekly Spending Report - {start_date.strftime('%b %d')} to {today.strftime('%b %d, %Y')}",
                "total_spent": 0,
                "transaction_count": 0,
                "top_merchants": [],
                "category_breakdown": {},
                "html_body": "<p>No transactions this week.</p>"
            }

        total_spent = self.calculate_total_spending(transactions)
        category_breakdown = self.calculate_totals_by_category(transactions)
        top_merchants = self.get_top_merchants(transactions, limit=5)

        # Get previous week for comparison
        prev_week_start = start_date - timedelta(days=7)
        prev_week_end = start_date - timedelta(days=1)
        prev_transactions = self.get_weekly_transactions(prev_week_end)
        prev_week_spent = self.calculate_total_spending(prev_transactions)

        # Calculate percentage change
        if prev_week_spent > 0:
            pct_change = ((total_spent - prev_week_spent) / prev_week_spent) * 100
        else:
            pct_change = 0

        html_body = self._generate_html_report(
            title="📊 WEEKLY SPENDING REPORT",
            date=f"{start_date.strftime('%b %d')} to {today.strftime('%b %d, %Y')}",
            total_spent=total_spent,
            transaction_count=len(transactions),
            top_merchants=top_merchants,
            category_breakdown=category_breakdown,
            comparison={"prev_week": prev_week_spent, "pct_change": pct_change}
        )

        return {
            "subject": f"Weekly Spending Report - {start_date.strftime('%b %d')} to {today.strftime('%b %d, %Y')}",
            "total_spent": total_spent,
            "transaction_count": len(transactions),
            "top_merchants": top_merchants,
            "category_breakdown": category_breakdown,
            "html_body": html_body
        }

    def format_monthly_report(self):
        """Generate formatted monthly spending report"""
        today = datetime.now()
        year, month = today.year, today.month
        transactions = self.get_monthly_transactions(year, month)

        if not transactions:
            month_name = today.strftime('%B %Y')
            return {
                "subject": f"Monthly Spending Report - {month_name}",
                "total_spent": 0,
                "transaction_count": 0,
                "top_merchants": [],
                "category_breakdown": {},
                "html_body": f"<p>No transactions in {month_name}.</p>"
            }

        total_spent = self.calculate_total_spending(transactions)
        category_breakdown = self.calculate_totals_by_category(transactions)
        top_merchants = self.get_top_merchants(transactions, limit=5)

        # Get previous month for comparison
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

        prev_transactions = self.get_monthly_transactions(prev_year, prev_month)
        prev_month_spent = self.calculate_total_spending(prev_transactions)

        # Calculate percentage change
        if prev_month_spent > 0:
            pct_change = ((total_spent - prev_month_spent) / prev_month_spent) * 100
        else:
            pct_change = 0

        month_name = datetime(year, month, 1).strftime('%B %Y')

        html_body = self._generate_html_report(
            title="📊 MONTHLY SPENDING REPORT",
            date=month_name,
            total_spent=total_spent,
            transaction_count=len(transactions),
            top_merchants=top_merchants,
            category_breakdown=category_breakdown,
            comparison={"prev_month": prev_month_spent, "pct_change": pct_change}
        )

        return {
            "subject": f"Monthly Spending Report - {month_name}",
            "total_spent": total_spent,
            "transaction_count": len(transactions),
            "top_merchants": top_merchants,
            "category_breakdown": category_breakdown,
            "html_body": html_body
        }

    def _generate_html_report(self, title, date, total_spent, transaction_count, top_merchants,
                             category_breakdown, comparison=None):
        """Generate HTML formatted report"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 20px auto; background: white; padding: 20px; border-radius: 8px; }}
                .header {{ text-align: center; color: #333; margin-bottom: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #4CAF50; }}
                .section-title {{ font-weight: bold; color: #4CAF50; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                .total {{ font-weight: bold; font-size: 18px; color: #d32f2f; }}
                .percentage {{ color: #4CAF50; }}
                .percentage.negative {{ color: #d32f2f; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{title}</h2>
                    <p>{date}</p>
                </div>

                <div class="section">
                    <div class="section-title">💰 TOTAL SPENDING</div>
                    <p class="total">₹{total_spent:,.2f}</p>
                    <p>Transactions: {transaction_count}</p>
        """

        # Add comparison if available
        if comparison:
            if 'prev_week' in comparison:
                prev_label = "Last Week"
                prev_amount = comparison['prev_week']
            else:
                prev_label = "Last Month"
                prev_amount = comparison['prev_month']

            pct_change = comparison['pct_change']
            pct_class = "percentage negative" if pct_change > 0 else "percentage"
            pct_symbol = "↑" if pct_change > 0 else "↓"

            html += f"""
                    <p>{prev_label}: ₹{prev_amount:,.2f}</p>
                    <p class="{pct_class}">{pct_symbol} {abs(pct_change):.1f}% vs {prev_label}</p>
            """

        # Top merchants section
        html += """
                </div>

                <div class="section">
                    <div class="section-title">📌 TOP MERCHANTS</div>
                    <table>
        """

        for merchant, amount in top_merchants:
            html += f"<tr><td>{merchant}</td><td>₹{amount:,.2f}</td></tr>"

        html += """
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">🏷️ BY CATEGORY</div>
                    <table>
        """

        # Sort categories by amount
        sorted_categories = sorted(category_breakdown.items(),
                                  key=lambda x: x[1]['amount'],
                                  reverse=True)

        for category, data in sorted_categories:
            amount = data['amount']
            count = data['count']
            pct = (amount / total_spent * 100) if total_spent > 0 else 0
            html += f"<tr><td>{category} ({count})</td><td>₹{amount:,.2f} ({pct:.1f}%)</td></tr>"

        html += """
                    </table>
                </div>
            </div>
        </body>
        </html>
        """

        return html
