@echo off
REM Daily Report Batch Script for Windows Task Scheduler
REM This script runs at 11:00 PM every day
REM Location: D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\

cd /d "D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker"

REM Log the execution time
echo Daily Report - Execution Time: %date% %time% >> logs\scheduler.log

REM Run the Python script to send daily report
python -c "from email_alerts import send_daily_report; send_daily_report()" 2>> logs\scheduler_error.log

REM Log completion
echo Daily Report - Completed: %date% %time% >> logs\scheduler.log

REM Exit
exit /b 0
