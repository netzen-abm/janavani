import smtplib
import os
import logging
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger("janavani.services.watchdog")

class JanavaniAlertWatchdog:
    """
    Monitors operations thresholds across system pipelines.
    Triggers direct warning matrices to team contacts if anomalies pass tolerance marks.
    """
    def __init__(self):
        # Configuration keys securely extracted via environment profile bindings
        self.smtp_server = os.getenv("SMTP_SERVER_HOST", "smtp.janavani.internal")
        self.smtp_port = int(os.getenv("SMTP_SERVER_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_SECURITY_USER", "")
        self.smtp_pass = os.getenv("SMTP_SECURITY_PASSWORD", "")
        self.alert_recipient = "ops-alerts@janavani.org"

    def dispatch_incident_email(self, service_channel: str, error_rate: float, execution_count: int) -> bool:
        """Issues email warning vectors if downstream service error metrics breach system safety targets."""
        if not self.smtp_user or not self.smtp_pass:
            logger.warning("SMTP credentials unpopulated. Bypassing incident alert routing.")
            return False

        message_body = (
            f"⚠️ JANAVANI ANOMALY SPARK DETECTED\n"
            f"=========================================\n"
            f"Timestamp (UTC): {datetime.utcnow().isoformat()}\n"
            f"Target Channel : {service_channel}\n"
            f"Current Faults : {error_rate:.2f}%\n"
            f"Total Queries  : {execution_count} requests evaluated inside tracking window.\n\n"
            f"Action Required: Audit isolated docker compose logs via terminal using standard commands."
        )

        msg = MIMEText(message_body)
        msg["Subject"] = f"[CRITICAL CRASH ALERT] Pipeline Failure Spill: {service_channel}"
        msg["From"] = f"watchdog@{os.getenv('DOMAIN_NAME', 'janavani.internal')}"
        msg["To"] = self.alert_recipient

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls() # Enforce cryptographically secured transport tunnels
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(msg["From"], [self.alert_recipient], msg.as_string())
            logger.info(f"Incident validation alert issued successfully to {self.alert_recipient}")
            return True
        except Exception as mail_fault:
            logger.error(f"Failed to transmit emergency infrastructure warning packet: {str(mail_fault)}")
            return False
