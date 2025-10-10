# utils.py

import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def generate_otp():
    """
    Generates a 4-digit random OTP as a string.
    """
    return str(random.randint(1000, 100000))

def send_otp_email(user): 
    """
    Generates an OTP, saves it to the user model, and sends it via email.
    Takes a user object as an argument.
    """
    otp = generate_otp()
    
    # Save OTP and timestamp to the user model
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()

    subject = 'Your Account Verification OTP'
    message = f'Hello {user.full_name},\n\nYour One-Time Password (OTP) for account verification is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nThank you.'
    
    try:
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        # In a real application, you should log this error
        print(f"Failed to send email to {user.email}: {e}")