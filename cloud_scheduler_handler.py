"""
Google Cloud Scheduler Handler
Receives HTTP requests from Cloud Scheduler and sends reports
This runs as a Flask app that Cloud Scheduler can call
"""
from flask import Flask, request, jsonify
from email_alerts import send_daily_report, send_weekly_report, send_monthly_report
from logger import log
import os
from functools import wraps

app = Flask(__name__)

# Simple API key for security
SCHEDULER_API_KEY = os.getenv("SCHEDULER_API_KEY", "your-secret-key-here")

def require_api_key(f):
    """Decorator to check API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != SCHEDULER_API_KEY:
            log.warning("Unauthorized Cloud Scheduler request")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/schedule/daily-report", methods=["POST"])
@require_api_key
def send_daily():
    """Endpoint for daily report (Cloud Scheduler calls this)"""
    try:
        log.info("[Cloud Scheduler] Sending daily report...")
        result = send_daily_report()

        if result:
            log.info("[Cloud Scheduler] Daily report sent successfully")
            return jsonify({
                "status": "success",
                "message": "Daily report sent",
                "timestamp": str(__import__('datetime').datetime.now())
            }), 200
        else:
            log.error("[Cloud Scheduler] Daily report failed")
            return jsonify({
                "status": "error",
                "message": "Failed to send daily report"
            }), 500

    except Exception as e:
        log.error(f"[Cloud Scheduler] Daily report error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/schedule/weekly-report", methods=["POST"])
@require_api_key
def send_weekly():
    """Endpoint for weekly report"""
    try:
        log.info("[Cloud Scheduler] Sending weekly report...")
        result = send_weekly_report()

        if result:
            log.info("[Cloud Scheduler] Weekly report sent successfully")
            return jsonify({
                "status": "success",
                "message": "Weekly report sent",
                "timestamp": str(__import__('datetime').datetime.now())
            }), 200
        else:
            log.error("[Cloud Scheduler] Weekly report failed")
            return jsonify({
                "status": "error",
                "message": "Failed to send weekly report"
            }), 500

    except Exception as e:
        log.error(f"[Cloud Scheduler] Weekly report error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/schedule/monthly-report", methods=["POST"])
@require_api_key
def send_monthly():
    """Endpoint for monthly report"""
    try:
        log.info("[Cloud Scheduler] Sending monthly report...")
        result = send_monthly_report()

        if result:
            log.info("[Cloud Scheduler] Monthly report sent successfully")
            return jsonify({
                "status": "success",
                "message": "Monthly report sent",
                "timestamp": str(__import__('datetime').datetime.now())
            }), 200
        else:
            log.error("[Cloud Scheduler] Monthly report failed")
            return jsonify({
                "status": "error",
                "message": "Failed to send monthly report"
            }), 500

    except Exception as e:
        log.error(f"[Cloud Scheduler] Monthly report error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": str(__import__('datetime').datetime.now())
    }), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    log.info(f"Starting Cloud Scheduler Handler on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
