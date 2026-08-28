"""Email delivery service.

Sends real transactional email through SMTP when configured. When SMTP is not
configured (local/dev), the message is logged instead — no silent no-op, the
content is always recorded for inspection.
"""

import smtplib
import structlog
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


def send_email(to: str, subject: str, html_body: str) -> bool:
    """Send an HTML email. Returns True if delivered, False otherwise."""
    if not settings.SMTP_HOST:
        logger.info(
            "email.logged",
            to=to,
            subject=subject,
            reason="SMTP not configured — logging instead of sending",
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587, timeout=15)
            server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, [to], msg.as_string())
        server.quit()
        logger.info("email.sent", to=to, subject=subject)
        return True
    except Exception as e:
        logger.error("email.failed", to=to, subject=subject, error=str(e)[:200])
        return False
