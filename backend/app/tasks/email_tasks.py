"""
Email-related background tasks (Celery, optional).
"""
import structlog
from app.tasks import celery_app
from app.config import get_settings
from typing import List, Optional

settings = get_settings()
logger = structlog.get_logger()


if celery_app is not None:

    @celery_app.task(bind=True, max_retries=3)
    def send_email_task(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        """Send an email."""
        try:
            logger.info(
                "email.task.start",
                to_emails=to_emails,
                subject=subject,
            )

            # In a real implementation, we'd use an email service like SendGrid, SES, etc.
            # For now, we just log the email as a placeholder.
            logger.info(
                "email.task.sent",
                to_emails=to_emails,
                subject=subject,
                body_length=len(body),
                html_body_length=len(html_body) if html_body else 0,
            )

            return {
                "status": "success",
                "to_emails": to_emails,
                "subject": subject,
                "message_id": f"<{hash(str(to_emails) + subject)}@dsir.dev>",
            }

        except Exception as exc:
            logger.error(
                "email.task.failure",
                to_emails=to_emails,
                subject=subject,
                error=str(exc),
            )

            if self.request.retries < self.max_retries:
                raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)

            return {
                "status": "failure",
                "to_emails": to_emails,
                "subject": subject,
                "error": str(exc),
            }

    @celery_app.task(bind=True)
    def send_welcome_email_task(self, user_email: str, user_name: str):
        """Send welcome email to new user."""
        return send_email_task(
            to_emails=[user_email],
            subject="Welcome to DSir!",
            body=f"Hello {user_name},\n\nWelcome to DSir, the best AI-powered programming education platform!",
            html_body=f"<h1>Hello {user_name}!</h1><p>Welcome to DSir, the best AI-powered programming education platform!</p>",
        )

    @celery_app.task(bind=True)
    def send_course_enrollment_email_task(self, user_email: str, user_name: str, course_title: str):
        """Send course enrollment confirmation email."""
        return send_email_task(
            to_emails=[user_email],
            subject=f"Enrolled in {course_title}",
            body=f"Hello {user_name},\n\nYou have successfully enrolled in the course: {course_title}",
            html_body=f"<h1>Hello {user_name}!</h1><p>You have successfully enrolled in the course: <strong>{course_title}</strong></p>",
        )
