"""
Enhanced Report Generator with Charts & Visualizations
Generates dashboard-style reports with matplotlib charts embedded as base64
"""
from report_generator import ReportGenerator
import matplotlib.pyplot as plt
import matplotlib
import base64
import io
from datetime import datetime, timedelta

matplotlib.use('Agg')  # Use non-interactive backend for server environments

class EnhancedReportGenerator(ReportGenerator):
    """Extended ReportGenerator with chart visualizations"""

    def _fig_to_base64(self, fig):
        """Convert matplotlib figure to base64 encoded string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        return image_base64

    def _create_category_pie_chart(self, category_breakdown):
        """Create pie chart for category distribution"""
        if not category_breakdown:
            return None

        categories = list(category_breakdown.keys())
        amounts = [cat['amount'] for cat in category_breakdown.values()]

        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors[:len(categories)], startangle=90)
        ax.set_title('Spending by Category', fontsize=14, fontweight='bold')

        return self._fig_to_base64(fig)

    def _create_merchants_chart(self, top_merchants):
        """Create bar chart for top merchants"""
        if not top_merchants:
            return None

        merchants = [m[0][:20] for m in top_merchants]  # Truncate long names
        amounts = [m[1] for m in top_merchants]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(merchants, amounts, color='#4ECDC4')
        ax.set_xlabel('Amount (Rs)', fontsize=11, fontweight='bold')
        ax.set_title('Top Merchants', fontsize=14, fontweight='bold')
        ax.invert_yaxis()

        # Add value labels on bars
        for i, v in enumerate(amounts):
            ax.text(v + 100, i, f'Rs {v:,.0f}', va='center', fontsize=9)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _create_daily_trend_chart(self, end_date=None, days=7):
        """Create line chart for daily spending trend (last N days)"""
        if end_date is None:
            end_date = datetime.now().date()

        daily_amounts = []
        daily_labels = []

        for i in range(days - 1, -1, -1):
            current_date = end_date - timedelta(days=i)
            transactions = self.get_daily_transactions(current_date)
            daily_amount = self.calculate_total_spending(transactions)
            daily_amounts.append(daily_amount)
            daily_labels.append(current_date.strftime('%m-%d'))

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(daily_labels, daily_amounts, marker='o', linewidth=2, markersize=8, color='#FF6B6B')
        ax.fill_between(range(len(daily_labels)), daily_amounts, alpha=0.3, color='#FF6B6B')
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax.set_ylabel('Amount (Rs)', fontsize=11, fontweight='bold')
        ax.set_title('Daily Spending Trend', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Rotate x labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def format_daily_report_enhanced(self):
        """Generate enhanced daily report with charts"""
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
        total_income = self.calculate_total_income(transactions)
        category_breakdown = self.calculate_totals_by_category(transactions)
        top_merchants = self.get_top_merchants(transactions, limit=5)

        # Generate charts
        category_chart = self._create_category_pie_chart(category_breakdown)
        merchants_chart = self._create_merchants_chart(top_merchants)
        trend_chart = self._create_daily_trend_chart(today, days=7)

        # Generate HTML with charts
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fa; margin: 0; padding: 0; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header p {{ margin: 5px 0; font-size: 14px; opacity: 0.9; }}
                .stats {{ display: flex; justify-content: space-around; padding: 20px; background: #f8f9fa; border-bottom: 2px solid #e0e0e0; }}
                .stat-card {{ text-align: center; flex: 1; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
                .section {{ padding: 25px; border-bottom: 1px solid #e0e0e0; }}
                .section-title {{ font-size: 16px; font-weight: bold; color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                .chart-container {{ text-align: center; margin: 20px 0; }}
                .chart-container img {{ max-width: 100%; height: auto; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th {{ background: #f0f0f0; padding: 12px; text-align: left; font-weight: bold; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                tr:hover {{ background: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; background: #f8f9fa; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Daily Spending Report</h1>
                    <p>{today.strftime('%A, %B %d, %Y')}</p>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">Rs {total_spent:,.2f}</div>
                        <div class="stat-label">Total Spent</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(transactions)}</div>
                        <div class="stat-label">Transactions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Rs {total_income:,.2f}</div>
                        <div class="stat-label">Total Income</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Rs {(total_income - total_spent):,.2f}</div>
                        <div class="stat-label">Net Balance</div>
                    </div>
                </div>
        """

        # Add category pie chart
        if category_chart:
            html_body += f"""
                <div class="section">
                    <div class="section-title">Spending by Category</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{category_chart}" alt="Category Chart">
                    </div>
                </div>
            """

        # Add merchants bar chart
        if merchants_chart:
            html_body += f"""
                <div class="section">
                    <div class="section-title">Top Merchants</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{merchants_chart}" alt="Merchants Chart">
                    </div>
                </div>
            """

        # Add trend chart
        if trend_chart:
            html_body += f"""
                <div class="section">
                    <div class="section-title">7-Day Spending Trend</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{trend_chart}" alt="Trend Chart">
                    </div>
                </div>
            """

        # Add category breakdown table
        html_body += """
                <div class="section">
                    <div class="section-title">Category Breakdown</div>
                    <table>
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Amount</th>
                                <th>Transactions</th>
                                <th>Percentage</th>
                            </tr>
                        </thead>
                        <tbody>
        """

        for category, data in sorted(category_breakdown.items(), key=lambda x: x[1]['amount'], reverse=True):
            amount = data['amount']
            count = data['count']
            pct = (amount / total_spent * 100) if total_spent > 0 else 0
            html_body += f"""
                            <tr>
                                <td>{category}</td>
                                <td>Rs {amount:,.2f}</td>
                                <td>{count}</td>
                                <td>{pct:.1f}%</td>
                            </tr>
            """

        html_body += """
                        </tbody>
                    </table>
                </div>

                <div class="footer">
                    <p>SMS Budget Tracker - Automated Spending Report</p>
                    <p>This report was generated automatically. Check your dashboard for more details.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return {
            "subject": f"Daily Spending Report - {today.strftime('%B %d, %Y')}",
            "total_spent": total_spent,
            "transaction_count": len(transactions),
            "top_merchants": top_merchants,
            "category_breakdown": category_breakdown,
            "html_body": html_body
        }

    def format_weekly_report_enhanced(self):
        """Generate enhanced weekly report with charts"""
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
        total_income = self.calculate_total_income(transactions)
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

        change_indicator = f"↑ {pct_change:.1f}%" if pct_change > 0 else f"↓ {abs(pct_change):.1f}%"
        change_color = "#FF6B6B" if pct_change > 0 else "#4ECDC4"

        # Generate charts
        category_chart = self._create_category_pie_chart(category_breakdown)
        merchants_chart = self._create_merchants_chart(top_merchants)
        trend_chart = self._create_daily_trend_chart(today, days=7)

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fa; margin: 0; padding: 0; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header p {{ margin: 5px 0; font-size: 14px; opacity: 0.9; }}
                .stats {{ display: flex; justify-content: space-around; padding: 20px; background: #f8f9fa; border-bottom: 2px solid #e0e0e0; }}
                .stat-card {{ text-align: center; flex: 1; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
                .comparison {{ text-align: center; padding: 15px; background: #f9f9f9; margin: 10px; border-radius: 8px; }}
                .comparison-value {{ font-size: 20px; font-weight: bold; color: {change_color}; }}
                .section {{ padding: 25px; border-bottom: 1px solid #e0e0e0; }}
                .section-title {{ font-size: 16px; font-weight: bold; color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                .chart-container {{ text-align: center; margin: 20px 0; }}
                .chart-container img {{ max-width: 100%; height: auto; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th {{ background: #f0f0f0; padding: 12px; text-align: left; font-weight: bold; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                tr:hover {{ background: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; background: #f8f9fa; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Weekly Spending Report</h1>
                    <p>{start_date.strftime('%b %d')} to {today.strftime('%b %d, %Y')}</p>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">Rs {total_spent:,.2f}</div>
                        <div class="stat-label">Total Spent</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(transactions)}</div>
                        <div class="stat-label">Transactions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Rs {total_income:,.2f}</div>
                        <div class="stat-label">Total Income</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Rs {(total_income - total_spent):,.2f}</div>
                        <div class="stat-label">Net Balance</div>
                    </div>
                </div>

                <div class="comparison">
                    <div class="section-title">Comparison with Previous Week</div>
                    <div class="comparison-value">{change_indicator}</div>
                    <p>Previous Week: Rs {prev_week_spent:,.2f}</p>
                </div>
        """

        # Add category pie chart
        if category_chart:
            html_body += f"""
                <div class="section">
                    <div class="section-title">Spending by Category</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{category_chart}" alt="Category Chart">
                    </div>
                </div>
            """

        # Add merchants bar chart
        if merchants_chart:
            html_body += f"""
                <div class="section">
                    <div class="section-title">Top Merchants</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{merchants_chart}" alt="Merchants Chart">
                    </div>
                </div>
            """

        # Add trend chart
        if trend_chart:
            html_body += f"""
                <div class="section">
                    <div class="section-title">7-Day Spending Trend</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{trend_chart}" alt="Trend Chart">
                    </div>
                </div>
            """

        # Add category breakdown table
        html_body += """
                <div class="section">
                    <div class="section-title">Category Breakdown</div>
                    <table>
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Amount</th>
                                <th>Transactions</th>
                                <th>Percentage</th>
                            </tr>
                        </thead>
                        <tbody>
        """

        for category, data in sorted(category_breakdown.items(), key=lambda x: x[1]['amount'], reverse=True):
            amount = data['amount']
            count = data['count']
            pct = (amount / total_spent * 100) if total_spent > 0 else 0
            html_body += f"""
                            <tr>
                                <td>{category}</td>
                                <td>Rs {amount:,.2f}</td>
                                <td>{count}</td>
                                <td>{pct:.1f}%</td>
                            </tr>
            """

        html_body += """
                        </tbody>
                    </table>
                </div>

                <div class="footer">
                    <p>SMS Budget Tracker - Automated Spending Report</p>
                    <p>This report was generated automatically. Check your dashboard for more details.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return {
            "subject": f"Weekly Spending Report - {start_date.strftime('%b %d')} to {today.strftime('%b %d, %Y')}",
            "total_spent": total_spent,
            "transaction_count": len(transactions),
            "top_merchants": top_merchants,
            "category_breakdown": category_breakdown,
            "html_body": html_body
        }

    def format_monthly_report_enhanced(self):
        """Generate enhanced monthly report with charts"""
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
        total_income = self.calculate_total_income(transactions)
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

        change_indicator = f"↑ {pct_change:.1f}%" if pct_change > 0 else f"↓ {abs(pct_change):.1f}%"
        change_color = "#FF6B6B" if pct_change > 0 else "#4ECDC4"

        month_name = today.strftime('%B %Y')

        # Generate charts (daily trend for the month)
        category_chart = self._create_category_pie_chart(category_breakdown)
        merchants_chart = self._create_merchants_chart(top_merchants)

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fa; margin: 0; padding: 0; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .header p {{ margin: 5px 0; font-size: 14px; opacity: 0.9; }}
                .stats {{ display: flex; justify-content: space-around; padding: 20px; background: #f8f9fa; border-bottom: 2px solid #e0e0e0; }}
                .stat-card {{ text-align: center; flex: 1; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
                .comparison {{ text-align: center; padding: 15px; background: #f9f9f9; margin: 10px; border-radius: 8px; }}
                .comparison-value {{ font-size: 20px; font-weight: bold; color: {change_color}; }}
                .section {{ padding: 25px; border-bottom: 1px solid #e0e0e0; }}
                .section-title {{ font-size: 16px; font-weight: bold; color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                .chart-container {{ text-align: center; margin: 20px 0; }}
                .chart-container img {{ max-width: 100%; height: auto; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th {{ background: #f0f0f0; padding: 12px; text-align: left; font-weight: bold; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                tr:hover {{ background: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; background: #f8f9fa; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Monthly Spending Report</h1>
                    <p>{month_name}</p>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">Rs {total_spent:,.2f}</div>
                        <div class="stat-label">Total Spent</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(transactions)}</div>
                        <div class="stat-label">Transactions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Rs {total_income:,.2f}</div>
                        <div class="stat-label">Total Income</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Rs {(total_income - total_spent):,.2f}</div>
                        <div class="stat-label">Net Balance</div>
                    </div>
                </div>

                <div class="comparison">
                    <div class="section-title">Comparison with Previous Month</div>
                    <div class="comparison-value">{change_indicator}</div>
                    <p>Previous Month: Rs {prev_month_spent:,.2f}</p>
                </div>
        """

        # Add category pie chart
        if category_chart:
            html_body += f"""
                <div class="section">
                    <div class="section-title">Spending by Category</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{category_chart}" alt="Category Chart">
                    </div>
                </div>
            """

        # Add merchants bar chart
        if merchants_chart:
            html_body += f"""
                <div class="section">
                    <div class="section-title">Top Merchants</div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{merchants_chart}" alt="Merchants Chart">
                    </div>
                </div>
            """

        # Add category breakdown table
        html_body += """
                <div class="section">
                    <div class="section-title">Category Breakdown</div>
                    <table>
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Amount</th>
                                <th>Transactions</th>
                                <th>Percentage</th>
                            </tr>
                        </thead>
                        <tbody>
        """

        for category, data in sorted(category_breakdown.items(), key=lambda x: x[1]['amount'], reverse=True):
            amount = data['amount']
            count = data['count']
            pct = (amount / total_spent * 100) if total_spent > 0 else 0
            html_body += f"""
                            <tr>
                                <td>{category}</td>
                                <td>Rs {amount:,.2f}</td>
                                <td>{count}</td>
                                <td>{pct:.1f}%</td>
                            </tr>
            """

        html_body += """
                        </tbody>
                    </table>
                </div>

                <div class="footer">
                    <p>SMS Budget Tracker - Automated Spending Report</p>
                    <p>This report was generated automatically. Check your dashboard for more details.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return {
            "subject": f"Monthly Spending Report - {month_name}",
            "total_spent": total_spent,
            "transaction_count": len(transactions),
            "top_merchants": top_merchants,
            "category_breakdown": category_breakdown,
            "html_body": html_body
        }
