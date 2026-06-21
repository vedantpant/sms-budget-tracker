# Windows Task Scheduler Setup Guide

## Overview
This guide shows how to set up Windows Task Scheduler to automatically send reports at:
- **Daily**: 11:00 PM every day
- **Weekly**: Sunday at 6:00 PM
- **Monthly**: 1st of month at 6:00 PM

## Prerequisites
✅ Windows 10/11
✅ Python installed and in PATH
✅ Report batch files created (send_daily_report.bat, etc.)
✅ .env file configured

---

## Step 1: Create Logs Directory

Open PowerShell and run:
```powershell
mkdir "D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\logs"
```

---

## Step 2: Open Task Scheduler

**Method 1: Press Windows Key + R, type:**
```
taskschd.msc
```

**Method 2: Search for "Task Scheduler" in Windows search**

---

## Step 3: Create Daily Report Task

### 3.1 Create New Task
- Right-click "Task Scheduler Library"
- Select "Create Basic Task"
- Name: `SMS Budget - Daily Report`
- Description: `Send daily spending report at 11 PM`

### 3.2 Set Trigger
- Click "Triggers" tab
- Click "New"
- Choose "Daily"
- Set time: `11:00 PM`
- Click "OK"

### 3.3 Set Action
- Click "Actions" tab
- Click "New"
- Program/script: `C:\Python\python.exe` (or your Python path)
- Add arguments: `-c "from email_alerts import send_daily_report; send_daily_report()"`
- Start in: `D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker`
- Click "OK"

### 3.4 Set Conditions
- Click "Conditions" tab
- Uncheck "Stop the task if it runs longer than"
- Check "Start the task only if the computer is on AC power" (optional)

### 3.5 Finish
- Click "OK" to save task

---

## Step 4: Create Weekly Report Task

### 4.1 Create New Task
- Name: `SMS Budget - Weekly Report`
- Description: `Send weekly spending report every Sunday at 6 PM`

### 4.2 Set Trigger
- Click "Triggers" tab
- Click "New"
- Choose "Weekly"
- Set day: `Sunday`
- Set time: `6:00 PM`
- Click "OK"

### 4.3 Set Action
- Click "Actions" tab
- Click "New"
- Program/script: `C:\Python\python.exe`
- Add arguments: `-c "from email_alerts import send_weekly_report; send_weekly_report()"`
- Start in: `D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker`
- Click "OK"

### 4.4 Finish
- Click "OK" to save task

---

## Step 5: Create Monthly Report Task

### 5.1 Create New Task
- Name: `SMS Budget - Monthly Report`
- Description: `Send monthly spending report on 1st at 6 PM`

### 5.2 Set Trigger
- Click "Triggers" tab
- Click "New"
- Choose "Monthly"
- Set to: `1st day of every month`
- Set time: `6:00 PM`
- Click "OK"

### 5.3 Set Action
- Click "Actions" tab
- Click "New"
- Program/script: `C:\Python\python.exe`
- Add arguments: `-c "from email_alerts import send_monthly_report; send_monthly_report()"`
- Start in: `D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker`
- Click "OK"

### 5.4 Finish
- Click "OK" to save task

---

## Step 6: Test Tasks

### Manual Test
1. Right-click each task
2. Select "Run"
3. Check your email for test reports

### Verify Logs
```
D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\logs\scheduler.log
D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\logs\scheduler_error.log
```

---

## Step 7: Verify Settings

### Check Running Tasks
```powershell
Get-ScheduledTask -TaskName "*SMS Budget*" | Get-ScheduledTaskInfo
```

### View Task Details
```powershell
Get-ScheduledTask -TaskName "SMS Budget - Daily Report" | Format-List
```

---

## Troubleshooting

### Task doesn't run
1. ✅ Check Python PATH is correct
2. ✅ Verify .env file has ALERT_EMAIL set
3. ✅ Check logs folder for errors
4. ✅ Run task manually to test

### Python not found
Find Python path:
```powershell
where python
```

Use full path in Task Scheduler:
```
C:\Python\python.exe  (or your actual path)
```

### No logs appear
Create logs folder manually:
```powershell
mkdir "D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\logs"
```

### Email not sent
1. Check ALERT_EMAIL in .env
2. Check Gmail app password is correct
3. Check internet connection
4. Review scheduler_error.log

---

## Features

✅ **Automatic Execution** - Runs at scheduled times
✅ **Survives Script Crashes** - Independent of listener.py
✅ **Logging** - All executions logged
✅ **Error Handling** - Error logs for debugging
✅ **Flexible Timing** - Easy to adjust times

⚠️ **Limitation** - Computer must be ON at scheduled time

---

## Optional: Run on Boot

To run listener.py on computer startup:

1. Create: `run_listener.bat`
```batch
@echo off
cd /d "D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker"
python listener.py
```

2. Create scheduled task:
   - Name: `SMS Budget - Listener Service`
   - Trigger: `At logon`
   - Action: Run `run_listener.bat`

---

## Next: Cloud Backup

For reports even when computer is OFF, see:
- `SETUP_CLOUD_SCHEDULER.md`

---

## Support

For issues:
1. Check logs/scheduler.log
2. Verify Python installation
3. Test batch file manually
4. Review .env configuration
