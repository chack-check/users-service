import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from domain.notifications.ports import NotificationSenderPort
from infrastructure.settings import settings, templates_loader

logger = logging.getLogger("uvicorn.error")


def _generate_email_message(from_: str, to: list[str], subject: str, message: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_
    msg["To"] = ", ".join(to)
    html = MIMEText(message, "html")
    msg.attach(html)
    return msg


def _get_smtp_server(is_tls: bool = False) -> smtplib.SMTP:
    if is_tls:
        context = ssl.create_default_context()
        return smtplib.SMTP_SSL(settings.smtp_host, int(settings.smtp_port), context=context)

    return smtplib.SMTP(settings.smtp_host, int(settings.smtp_port))


def send_email(from_: str, to: list[str], subject: str, message: str) -> None:
    server = _get_smtp_server(settings.smtp_use_tls)
    with server as s:
        if settings.smtp_password and settings.smtp_user:
            s.login(settings.smtp_user, settings.smtp_password)

        msg = _generate_email_message(from_, to, subject, message)
        s.sendmail(from_, to, msg.as_string())


class LoggingEmailSender(NotificationSenderPort):

    def __init__(self, adapter: NotificationSenderPort):
        self._adapter = adapter

    async def send_code(self, identifier: str, code: str) -> None:
        logger.debug(f"sending code message to email: {identifier=} {code=}")
        logger.debug(
            f"email smtp from: {settings.smtp_from}, smtp_host: {settings.smtp_host}, smtp_port: {settings.smtp_port}, smtp_tls: {settings.smtp_use_tls}"
        )
        try:
            await self._adapter.send_code(identifier, code)
        except Exception as e:
            logger.exception(e)
            raise


class EmailSender(NotificationSenderPort):

    def __init__(self, template: str = "email_verification.html"):
        self._template = template

    async def send_code(self, identifier: str, code: str) -> None:
        template_obj = templates_loader.get_template(self._template)
        loaded_template = template_obj.render({"code": code})
        subject = "Email verification code"
        send_email(settings.smtp_from, [identifier], subject, loaded_template)
