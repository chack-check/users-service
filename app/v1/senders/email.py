import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.project.settings import settings, templates_loader
from .base import BaseSender


def _generate_email_message(from_: str, to: list[str],
                            subject: str, message: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = to
    html = MIMEText(message, 'html')
    msg.attach(html)
    return msg


def _get_smtp_server(is_tls: bool = False) -> smtplib.SMTP:
    if is_tls:
        context = ssl.create_default_context()
        return smtplib.SMTP_SSL(
            settings.smtp_host, settings.smtp_port, context=context
        )

    return smtplib.SMTP(settings.smtp_host, settings.smtp_port)


def send_email(from_: str, to: list[str],
               subject: str, message: str) -> None:
    server = _get_smtp_server(settings.smtp_use_tls)
    with server as s:
        if settings.smtp_password:
            s.login(settings.smtp_user, settings.smtp_password)

        msg = _generate_email_message(from_, to, subject, message)
        s.sendmail(from_, to, msg.as_string())


class EmailSender(BaseSender):
    templates_subjects = {
        'email_verification.html': 'Email verification code'
    }

    def send_verification_code(self, to: list[str], code: str):
        template = 'email_verification.html'
        template_obj = templates_loader.get_template('email_verification.html')
        loaded_template = template_obj.render({'code': code})
        subject = self.templates_subjects[template]
        send_email(settings.smtp_from, to, subject, loaded_template)
