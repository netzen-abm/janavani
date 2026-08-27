"""Operational alerting for Janavani service health."""

from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

logger = logging.getLogger("janavani.services.watchdog")


class JanavaniAlertWatchdog:
    """Send operational alerts when configured thresholds are breached."""

    def __init__(self) -> None:
        self.smtp_server = os.getenv("SMTP_SERVER_HOST", "smtp.janavani.internal")
        self.smtp_port = int(os.getenv("SMTP_SERVER_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_SECURITY_USER", "")
        self.smtp_pass = os.getenv("SMTP_SECURITY_PASSWORD", "")
        self.alert_recipient = os.getenv("ALERT_RECIPIENT", "ops-alerts@janavani.org")

    def dispatch_incident_email(
        self, service_channel: str, error_rate: float, execution_count: int
    ) -> bool:
        """Send an incident alert when SMTP credentials are configured."""
        if not self.smtp_user or not self.smtp_pass:
            logger.warning("SMTP credentials are not configured; incident alert skipped.")
            return False

        message_body = (
            "JANAVANI ANOMALY DETECTED\n"
            "=========================\n"
            f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}\n"
            f"Target channel: {service_channel}\n"
            f"Current error rate: {error_rate:.2f}%\n"
            f"Execution count: {execution_count}\n"
        )
        return self._send(message_body, f"[Janavani] Incident: {service_channel}")

    def evaluate_sentiment_bounds_and_notify(
        self, office_id: str, average_rating: float
    ) -> bool:
        """Alert when an office satisfaction score falls below two stars."""
        if average_rating >= 2.0 or not self.smtp_user or not self.smtp_pass:
            return False

        message_body = (
            "JANAVANI ACCOUNTABILITY SCORE ALERT\n"
            "==================================\n"
            f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}\n"
            f"Target office: {office_id}\n"
            f"Current score: {average_rating:.2f} / 5.0\n"
        )
        return self._send(message_body, f"[Janavani] Accountability: {office_id}")

    def _send(self, body: str, subject: str) -> bool:
        """Send one email using the configured SMTP transport."""
        sender_domain = os.getenv("DOMAIN_NAME", "janavani.internal")
        sender = f"watchdog@{sender_domain}"
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = self.alert_recipient

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(sender, [self.alert_recipient], message.as_string())
            logger.info("Operational alert sent to %s", self.alert_recipient)
            return True
        except (OSError, smtplib.SMTPException) as exc:
            logger.error("Failed to send operational alert: %s", exc)
            return False
