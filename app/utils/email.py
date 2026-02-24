# app/utils/email.py
# app/utils/email.py
from flask_mail import Message
from flask import current_app
from threading import Thread
from app.extentions import mail
from app.utils.logger import logger

def send_email_async(to: str, subject: str, body: str):
    app = current_app._get_current_object()
    sender = app.config.get("MAIL_DEFAULT_SENDER")
    if not sender:
        raise ValueError("MAIL_DEFAULT_SENDER not configured")

    msg = Message(subject=subject, recipients=[to], body=body, sender=sender)

    def send(msg):
        with app.app_context():
            try:
                mail.send(msg)
                logger.info(f"[EMAIL SENT] → {msg.recipients}")
            except Exception as e:
                logger.error(f"[EMAIL SEND ERROR] {e}")

    Thread(target=send, args=(msg,)).start()
    
def send_email(to, subject, body):
    app = current_app._get_current_object()
    sender = app.config.get("MAIL_DEFAULT_SENDER")
    msg = Message(subject=subject, recipients=[to], body=body, sender=sender)
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(f"[EMAIL SENT] → {msg.recipients}")
        except Exception as e:
            logger.error(f"[EMAIL SEND ERROR] {e}")

