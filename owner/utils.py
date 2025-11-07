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
     
        print(f"Failed to send email to {user.email}: {e}")




# 
# Twilio SMS sending function
import random
import requests
from django.conf import settings

def generate_otp():
    """Generate a 4-digit OTP"""
    return str(random.randint(1000, 9999))


def send_otp_sms_infobip(phone_number, otp):
    """Send OTP SMS using Infobip API"""
    url = f"{settings.INFOBIP_BASE_URL}/sms/2/text/advanced"
    headers = {
        "Authorization": settings.INFOBIP_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "from": "MyApp",
                "destinations": [{"to": phone_number}],
                "text": f"Your OTP for password reset is {otp}. It will expire in 5 minutes."
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f" OTP sent successfully to {phone_number}")
            return True
        else:
            print("Failed to send OTP:", response.text)
            return False
    except Exception as e:
        print(" Infobip API Error:", e)
        return False

