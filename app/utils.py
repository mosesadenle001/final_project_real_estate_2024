from flask_mail import Message
from flask import url_for


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        'Password Reset Request',
        sender='noreply@yourdomain.com',
        recipients=[user.email]
    )
    msg.body = f'''To reset your password, visit the following link:{url_for('routes.reset_token', token=token, external=True)}
'''
    return msg

#print(msg)

