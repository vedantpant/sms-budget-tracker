@echo off
REM Weekly Report Batch Script for Windows Task Scheduler
REM This script runs every Sunday at 6:00 PM
REM Location: D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\

cd /d "D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker"

REM Log the execution time
echo Weekly Report - Execution Time: %date% %time% >> logs\scheduler.log

REM Run the Python script to send weekly report
python -c "from email_alerts import send_weekly_report; send_weekly_report()" 2>> logs\scheduler_error.log

REM Log completion
echo Weekly Report - Completed: %date% %time% >> logs\scheduler.log

REM Exit
exit /b 0
