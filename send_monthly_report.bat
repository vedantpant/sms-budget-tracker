@echo off
REM Monthly Report Batch Script for Windows Task Scheduler
REM This script runs on the 1st of every month at 6:00 PM
REM Location: D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\

cd /d "D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker"

REM Log the execution time
echo Monthly Report - Execution Time: %date% %time% >> logs\scheduler.log

REM Run the Python script to send monthly report
python -c "from email_alerts import send_monthly_report; send_monthly_report()" 2>> logs\scheduler_error.log

REM Log completion
echo Monthly Report - Completed: %date% %time% >> logs\scheduler.log

REM Exit
exit /b 0
