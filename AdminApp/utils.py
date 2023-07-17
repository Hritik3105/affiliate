from django.core.mail import send_mail
from django.conf import settings
import requests

def send_forget_password_mail(email,token):

    subject="your forget password link"
    message=f'Hi,click on the link to reset your passord http://127.0.0.1:8000/isadmin/change_password_link/{email}/{token}'
    email_from=settings.EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,message,email_from,recipient_list)
    return True

