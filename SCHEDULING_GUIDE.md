# Complete Report Scheduling Guide

## The Problem

How to ensure reports send at exact times even when:
- Computer is OFF
- Script is not running  
- Application crashes

---

## The Solution: 3-Layer Approach

```
┌─────────────────────────────────────┐
│   Google Cloud Scheduler (BACKUP)   │ ← Always on, cloud-based
│   Sends if computer is OFF          │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│ Windows Task Scheduler (PRIMARY)    │ ← Reliable, always on (if computer on)
│ Sends at exact times                │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│ listener.py (REAL-TIME)             │ ← Real-time SMS processing
│ Can send reports if running         │
└─────────────────────────────────────┘
```

---

## Implementation Timeline

### Immediate (30 minutes)
✅ Windows Task Scheduler setup
- Reliable for when computer is ON
- Detailed instructions in `SETUP_TASK_SCHEDULER.md`

### Optional (1-2 hours)
✅ Google Cloud Scheduler setup
- Cloud-based backup
- Works even when computer is OFF
- Detailed instructions in `SETUP_CLOUD_SCHEDULER.md`

---

## Quick Start

### Option 1: Windows Task Scheduler Only

**Best for:** Computer runs 24/7 or mostly on

**Setup time:** 30 minutes

**Steps:**
1. Read `SETUP_TASK_SCHEDULER.md`
2. Create 3 batch files (already created)
3. Create 3 scheduled tasks
4. Test each task

**Result:** Reports send at 11 PM, Sunday 6 PM, 1st 6 PM (if computer on)

---

### Option 2: Windows + Cloud (RECOMMENDED)

**Best for:** Maximum reliability, peace of mind

**Setup time:** 2-3 hours

**Steps:**
1. Set up Windows Task Scheduler (30 min)
2. Deploy to Google Cloud Run (1-2 hours)
3. Create 3 Cloud Scheduler jobs (30 min)
4. Test both systems

**Result:** 
- Reports send at exact times
- Works even if computer is OFF
- Fallback if one system fails

---

## Files Created

### Batch Scripts (for Task Scheduler)
```
send_daily_report.bat      → Runs at 11 PM
send_weekly_report.bat     → Runs Sunday 6 PM
send_monthly_report.bat    → Runs 1st 6 PM
```

### Cloud Handler
```
cloud_scheduler_handler.py → Flask app for Cloud Scheduler
```

### Setup Guides
```
SETUP_TASK_SCHEDULER.md    → Step-by-step Windows setup
SETUP_CLOUD_SCHEDULER.md   → Step-by-step Cloud setup
```

---

## Scheduling Specification

| Report | Frequency | Time | Method |
|--------|-----------|------|--------|
| Daily | Every day | 11:00 PM | Both |
| Weekly | Sunday | 6:00 PM | Both |
| Monthly | 1st of month | 6:00 PM | Both |

---

## Test Verification

### Windows Task Scheduler Test

1. Right-click task in Task Scheduler
2. Click "Run"
3. Check email within 2 minutes
4. Verify logs: `logs/scheduler.log`

### Cloud Scheduler Test

1. Go to Cloud Console
2. Click Cloud Scheduler job
3. Click "FORCE RUN"
4. Check email within 1 minute
5. Verify logs: Cloud Run logs

---

## Monitoring

### Windows Task Scheduler
```powershell
Get-ScheduledTask -TaskName "*SMS Budget*" | Get-ScheduledTaskInfo
```

### Cloud Scheduler
```bash
gcloud scheduler jobs list
gcloud run logs read sms-budget-handler --limit 50
```

### Local Logs
```
D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\logs\scheduler.log
D:\Vedant_Pant\Ultimate Personal Budget Manager\app_tracker\logs\scheduler_error.log
```

---

## Redundancy Matrix

| Scenario | Task Scheduler | Cloud Scheduler | listener.py |
|----------|---|---|---|
| Computer ON, App running | ✅ | ✅ | ✅ |
| Computer ON, App off | ✅ | ✅ | ❌ |
| Computer OFF | ❌ | ✅ | ❌ |
| Task Scheduler fails | ❌ | ✅ | ✅ |
| Cloud fails | ✅ | ❌ | ✅ |

**Result:** Multiple fallbacks ensure reports always send!

---

## Estimated Costs

### Windows Task Scheduler
- ✅ **FREE** (built-in to Windows)
- Requires: Computer on at scheduled time

### Google Cloud Scheduler
- ✅ **FREE** (3 jobs included)
- No additional cost for 3 report jobs
- Cloud Run: 2M free invocations/month

**Total cost:** $0 if computer stays on, or free Cloud tier otherwise

---

## Troubleshooting

### Reports not sending

**Check in order:**

1. **Task Scheduler:**
   - Is task enabled?
   - Is Python in PATH?
   - Check scheduler.log for errors

2. **Cloud Scheduler:**
   - Is service deployed?
   - Check execution history
   - Verify API key

3. **listener.py:**
   - Is script running?
   - Check logs for errors

### Email not received

1. Check ALERT_EMAIL in .env
2. Check Gmail spam folder
3. Verify Gmail app password
4. Check internet connection

### Duplicate reports

- This is normal if both systems run
- Your email will show both
- Supabase prevents double-counting
- You can disable one if unwanted

---

## Next Steps

### Recommended Order

1. **TODAY:** Set up Windows Task Scheduler
   - Read `SETUP_TASK_SCHEDULER.md`
   - Create 3 tasks
   - Test each one

2. **THIS WEEK:** Set up Cloud Scheduler (optional)
   - Read `SETUP_CLOUD_SCHEDULER.md`
   - Deploy cloud service
   - Create 3 jobs
   - Test and verify

3. **ONGOING:** Monitor and maintain
   - Check logs weekly
   - Verify tasks still running
   - Update timings if needed

---

## FAQs

**Q: Can I change the times?**
A: Yes! Edit the triggers in Task Scheduler or cron expressions in Cloud Scheduler

**Q: What if both send a report at same time?**
A: Safe! Email shows both, but only one transaction is recorded (duplicate protection)

**Q: Will it work if computer is turned off?**
A: Only with Cloud Scheduler. Task Scheduler requires computer to be ON.

**Q: Can I disable one system?**
A: Yes, but you lose the fallback. Not recommended.

**Q: What if I change my email?**
A: Update ALERT_EMAIL in .env and restart services

**Q: How do I know if it worked?**
A: Check email, verify logs, check Cloud Console

---

## Support

### Documentation
- Task Scheduler: `SETUP_TASK_SCHEDULER.md`
- Cloud: `SETUP_CLOUD_SCHEDULER.md`
- Code: `cloud_scheduler_handler.py`

### Logs
- Local: `logs/scheduler.log`
- Cloud: Cloud Console → Cloud Run logs
- Task Scheduler: Event Viewer → Windows Logs

---

## Summary

✅ **3 ways to send reports:**
1. Windows Task Scheduler (local, reliable)
2. Google Cloud Scheduler (cloud, always-on)
3. listener.py (real-time, fallback)

✅ **Maximum reliability:**
- Multiple redundancy
- Automatic fallbacks
- No single point of failure

✅ **Easy setup:**
- Step-by-step guides included
- 30 minutes to 2 hours total
- Zero cost (both options free)

---

**You now have a professional-grade report scheduling system!** 🚀
