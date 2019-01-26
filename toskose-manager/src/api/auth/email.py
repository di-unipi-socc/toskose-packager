from flask import render_template, current_app
from flask_babel import _
from flask_mail import Message

from api.main.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_jwt()
    send_email(
        '[Toskose Manager]: Reset your password',
        sender=app.config['ADMINS_EMAIL'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password_msg', user=user, token=token),
        html_body=render_template('email/reset_password_msg.html', user=user, token=token)
    )
