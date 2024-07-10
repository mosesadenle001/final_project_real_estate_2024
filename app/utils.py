from flask_mail import Message
from flask import url_for, current_app
import os
import secrets
from PIL import image

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        'Password Reset Request',
        sender='noreply@koredes.com',
        recipients=[user.email]
    )
    msg.body = f'''To reset your password, visit the following link:{url_for('routes.reset_token', token=token, external=True)}
'''
    return msg

#print(msg)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

