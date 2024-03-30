import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.project.settings import settings, templates_loader

from .base import BaseSender

logger = logging.getLogger("uvicorn.error")


def _generate_email_message(from_: str, to: list[str],
                            subject: str, message: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = ', '.join(to)
    html = MIMEText(message, 'html')
    msg.attach(html)
    return msg


def _get_smtp_server(is_tls: bool = False) -> smtplib.SMTP:
    logger.debug(f"Getting smtp server {is_tls=}")
    if is_tls:
        context = ssl.create_default_context()
        return smtplib.SMTP_SSL(
            settings.smtp_host, int(settings.smtp_port), context=context
        )

    return smtplib.SMTP(settings.smtp_host, int(settings.smtp_port))


def send_email(from_: str, to: list[str],
               subject: str, message: str) -> None:
    logger.debug(f"Sending email: {from_=} {to=} {subject=}")
    server = _get_smtp_server(settings.smtp_use_tls)
    with server as s:
        if settings.smtp_password and settings.smtp_user:
            logger.debug(f"Logging in smtp server with username and password")
            s.login(settings.smtp_user, settings.smtp_password)

        msg = _generate_email_message(from_, to, subject, message)
        s.sendmail(from_, to, msg.as_string())


class EmailSender(BaseSender):
    templates_subjects = {
        'email_verification.html': 'Email verification code'
    }

    def send_verification_code(self, to: list[str], code: str):
        template = 'email_verification.html'
        logger.debug(f"Sending verification code to email {to=} {code=} {template=}")
        template_obj = templates_loader.get_template('email_verification.html')
        loaded_template = template_obj.render({'code': code})
        subject = self.templates_subjects[template]
        send_email(settings.smtp_from, to, subject, loaded_template)
