# accounts/utils.py
import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():

    return str(random.randint(1000, 9999))

def send_otp_email(email, otp):

    subject = 'Your Account Verification OTP'
    message = f'Your OTP for verification is: {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)