import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import User

def generate_otp():
    """Generates a 4-digit random OTP."""
    return str(random.randint(1000, 9999))

def send_otp_email(user):
    """Generates, saves, and sends OTP to the user's email."""
    otp = generate_otp()
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()

    subject = 'Your Account Verification OTP'
    message = f'Hello {user.full_name},\n\nYour OTP for account verification is: {otp}\nThis OTP is valid for 5 minutes.\n\nThank you.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    send_mail(subject, message, from_email, recipient_list)