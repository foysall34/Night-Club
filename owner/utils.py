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



import requests
from django.conf import settings

def get_coordinates_from_city(city_name):
    url = f"https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": city_name,
        "apiKey": settings.GEOAPIFY_API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()

    if data["features"]:
        lat = data["features"][0]["properties"]["lat"]
        lon = data["features"][0]["properties"]["lon"]
        return lat, lon
    
    return None, None


from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in KM
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
