from sync_engine import SyncEngine
import time
from logger import log
import signal
from email_alerts import send_transaction_alert, send_error_alert

class Listener:

    def __init__(self):
        self.engine = SyncEngine()
        self.poll_interval = 60  # seconds
        self.running = False
        self._cycle_count = 0
        self._total_processed = 0
        self.heartbeat_every = 10


    def _poll(self):
        result = self.engine.process_pending()

        if result['success'] > 0 or result['failed'] > 0:
            self._total_processed += result['success']
            log.info(f"✓{result['success']} processed, ✗{result['failed']} failed")
        else:
            log.debug("No pending SMS found")

    def start(self):
        self.running = True
        log.info("Listener started, Press CTRL+C to stop.")

        while self.running:
            self._poll()
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
