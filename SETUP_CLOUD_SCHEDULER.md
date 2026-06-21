# Google Cloud Scheduler Setup Guide

## Overview
This guide sets up Google Cloud Scheduler as a **backup** for sending reports even when your computer is OFF.

**Why Cloud Scheduler?**
- ✅ Runs in the cloud (always on)
- ✅ Works when your computer is off
- ✅ Backup if Windows Task Scheduler fails
- ✅ Reliable HTTP-based triggering
- ✅ Free tier available (3 jobs)

---

## Prerequisites

1. **Google Account** (free)
2. **Google Cloud Project** (free tier)
3. **Flask installed** (for local testing)
4. **Cloud Run deployment** (optional, free)

---

## Option 1: Deploy to Google Cloud Run (Recommended)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "NEW PROJECT"
3. Name: `SMS Budget Tracker`
4. Click "CREATE"

### Step 2: Enable Required APIs

1. Search for "Cloud Run"
2. Click "Cloud Run API" → "ENABLE"

### Step 3: Create Dockerfile

Create `Dockerfile` in your project:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "cloud_scheduler_handler.py"]
```

### Step 4: Create requirements.txt

```
flask==2.3.0
python-dotenv==1.0.0
supabase==1.0.3
gunicorn==20.1.0
```

### Step 5: Deploy to Cloud Run

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project SMS-Budget-Tracker

# Deploy
gcloud run deploy sms-budget-handler `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars SCHEDULER_API_KEY=your-secret-key-here
```

### Step 6: Note the Service URL
The deployment will return a URL like:
```
https://sms-budget-handler-xxxxx.run.app
```

---

## Option 2: Deploy to Heroku (Free Alternative)

### Step 1: Create Heroku Account
- Go to [Heroku.com](https://www.heroku.com/)
- Sign up (free)

### Step 2: Create Procfile

Create `Procfile`:
```
web: gunicorn cloud_scheduler_handler:app
```

### Step 3: Deploy

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create sms-budget-tracker
git push heroku main
heroku config:set SCHEDULER_API_KEY=your-secret-key-here
```

Service URL: `https://sms-budget-tracker.herokuapp.com`

---

## Step 7: Create Cloud Scheduler Jobs

### Job 1: Daily Report

1. Go to [Cloud Scheduler](https://console.cloud.google.com/cloudscheduler)
2. Click "CREATE JOB"
3. Configure:
   - **Name:** `sms-daily-report`
   - **Frequency:** `0 23 * * *` (11 PM daily)
   - **Timezone:** (select your timezone)
4. Click "CREATE"
5. Click the job and "EDIT"
6. Set execution:
   - **Type:** HTTP
   - **URL:** `https://your-service-url/schedule/daily-report`
   - **HTTP Method:** POST
   - **Headers:** Add header
     - **Key:** `X-API-Key`
     - **Value:** `your-secret-key-here`
7. Click "UPDATE"

### Job 2: Weekly Report

1. Click "CREATE JOB"
2. Configure:
   - **Name:** `sms-weekly-report`
   - **Frequency:** `0 18 * * 0` (Sunday 6 PM)
   - **Timezone:** (select your timezone)
3. Click "CREATE"
4. Follow same execution setup as above
5. **URL:** `https://your-service-url/schedule/weekly-report`

### Job 3: Monthly Report

1. Click "CREATE JOB"
2. Configure:
   - **Name:** `sms-monthly-report`
   - **Frequency:** `0 18 1 * *` (1st of month 6 PM)
   - **Timezone:** (select your timezone)
3. Click "CREATE"
4. Follow same execution setup
5. **URL:** `https://your-service-url/schedule/monthly-report`

---

## Step 8: Test Cloud Scheduler Jobs

### Test via Cloud Console

1. Go to Cloud Scheduler
2. Find `sms-daily-report` job
3. Click the three dots (⋮)
4. Click "FORCE RUN"
5. Check your email for test report

### Verify via Logs

```bash
gcloud run logs read sms-budget-handler --limit 50
```

---

## Step 9: Update .env

Add to `.env`:
```
SCHEDULER_API_KEY=your-secret-key-here
```

Generate a strong key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Step 10: Monitor Cloud Scheduler

### Check Execution History

```bash
gcloud scheduler jobs describe sms-daily-report --location=us-central1
```

### View Recent Executions

1. Go to Cloud Console
2. Navigate to Cloud Scheduler
3. Click job name
4. View "Execution history"

---

## Pricing

✅ **Free Tier:**
- 3 jobs included free
- 1440 invocations/month per job
- Sufficient for daily, weekly, monthly reports

**If you need more:**
- Additional jobs: $0.10 per job per month
- Cloud Run: 2 million free invocations/month

---

## Hybrid Setup (Recommended)

### Windows Task Scheduler + Cloud Scheduler

**Why both?**
- Task Scheduler runs when computer is ON
- Cloud Scheduler runs when computer is OFF
- If one fails, the other acts as backup

**Setup:**
1. ✅ Configure Windows Task Scheduler (local)
2. ✅ Configure Cloud Scheduler (cloud)
3. Both will send reports independently

**Note:** Reports might send twice if both run simultaneously. This is safe - duplicates are handled.

---

## Troubleshooting

### Cloud Run logs show errors

```bash
gcloud run logs read sms-budget-handler --tail=100
```

### Reports not sending

1. Check Cloud Scheduler execution history
2. Verify API key in job headers
3. Check service logs
4. Test locally: `python cloud_scheduler_handler.py`

### Authentication errors

Verify:
- X-API-Key header is present
- API key matches SCHEDULER_API_KEY in .env
- Service deployed with correct env vars

### Service URL not reachable

1. Make sure service is deployed
2. Check Cloud Run status
3. Verify region is correct

---

## Next Steps

1. ✅ Deploy cloud service (Cloud Run or Heroku)
2. ✅ Create 3 Cloud Scheduler jobs
3. ✅ Test each job manually
4. ✅ Verify reports send to email
5. ✅ Monitor logs for 1 week

---

## Final Verification

### Test Checklist

- [ ] Windows Task Scheduler jobs created
- [ ] Cloud service deployed and healthy
- [ ] Cloud Scheduler jobs created
- [ ] Manual test: Daily report sent
- [ ] Manual test: Weekly report sent
- [ ] Manual test: Monthly report sent
- [ ] Logs verified (scheduler.log)
- [ ] Email received all 3 test reports

---

## Backup Plan

If Cloud Scheduler fails:
- Windows Task Scheduler still runs (if computer is on)
- Reports still send via listener.py (if running)
- Manually trigger via Cloud Console

If Windows Task Scheduler fails:
- Cloud Scheduler still runs (always on)
- Reports still send automatically

**Result: Maximum reliability with fallback options!**
