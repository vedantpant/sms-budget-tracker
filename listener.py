from sync_engine import SyncEngine
import time
from logger import log
import signal
from datetime import datetime
from email_alerts import send_transaction_alert, send_error_alert, send_daily_report, send_weekly_report, send_monthly_report

class Listener:

    def __init__(self):
        self.engine = SyncEngine()
        self.poll_interval = 60  # seconds
        self.running = False
        self._cycle_count = 0
        self._total_processed = 0
        self.heartbeat_every = 10

        # Report timing
        self.last_daily_report = None
        self.last_weekly_report = None
        self.last_monthly_report = None


    def _poll(self):
        result = self.engine.process_pending()

        if result['success'] > 0 or result['failed'] > 0:
            self._total_processed += result['success']
            log.info(f"✓{result['success']} processed, ✗{result['failed']} failed")
        else:
            log.debug("No pending SMS found")

    def _check_and_send_reports(self):
        """Check if it's time to send daily/weekly/monthly reports"""
        now = datetime.now()

        # Check daily report (11 PM)
        if self._should_send_daily_report(now):
            log.info("📊 Sending daily report...")
            send_daily_report()
            self.last_daily_report = now

        # Check weekly report (Sunday 6 PM)
        if self._should_send_weekly_report(now):
            log.info("📊 Sending weekly report...")
            send_weekly_report()
            self.last_weekly_report = now

        # Check monthly report (1st of month 6 PM)
        if self._should_send_monthly_report(now):
            log.info("📊 Sending monthly report...")
            send_monthly_report()
            self.last_monthly_report = now

    def _should_send_daily_report(self, now):
        """Check if it's time for daily report (11 PM)"""
        # Send if current hour is 23 (11 PM) and we haven't sent today
        if now.hour == 23 and now.minute >= 0:
            if self.last_daily_report is None or self.last_daily_report.date() != now.date():
                return True
        return False

    def _should_send_weekly_report(self, now):
        """Check if it's time for weekly report (Sunday 6 PM)"""
        # Sunday is weekday 6, 6 PM is hour 18
        if now.weekday() == 6 and now.hour == 18 and now.minute >= 0:
            if self.last_weekly_report is None or (now - self.last_weekly_report).days >= 7:
                return True
        return False

    def _should_send_monthly_report(self, now):
        """Check if it's time for monthly report (1st of month 6 PM)"""
        # 1st of month is day 1, 6 PM is hour 18
        if now.day == 1 and now.hour == 18 and now.minute >= 0:
            if self.last_monthly_report is None or now.month != self.last_monthly_report.month:
                return True
        return False

    def start(self):
        self.running = True
        log.info("Listener started, Press CTRL+C to stop.")

        while self.running:
            self._poll()
            self._check_and_send_reports()  # Check if it's time for reports
            self._cycle_count += 1

            if self._cycle_count % self.heartbeat_every == 0:  # Log heartbeat every 10 cycles
                self._heartbeat()

            self._interruptible_sleep()

    def stop(self):
        self.running = False
        log.info("Listener stopping...")

    def _interruptible_sleep(self):
        for _ in range(self.poll_interval):
            if not self.running:
                break
            time.sleep(1)

    def _heartbeat(self):
        log.info(
            f"[Heartbeat] Cycles: {self._cycle_count} | "
            f"Processed: {self._total_processed} | "
            f"Uptime: {self._cycle_count * self.poll_interval // 60} minutes"
        )



def main():
    listener = Listener()

    def _handle_signal(signum, frame):
        listener.stop()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    listener.start()
    log.info("Listener shutdown complete.")

if __name__ == "__main__":
    main()
