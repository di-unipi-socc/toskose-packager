from flask_mail import Message
from app import mail

from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset(user):
    token = user.get_reset_password_jwt()
    send_email(
        '[Toskose Manager]: Reset your password',
        sender=app.config['ADMINS_EMAIL'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password_msg', user=user, token=token)
        html_body=render_template('email/reset_password_msg.html', user=user, token=token)
    )
