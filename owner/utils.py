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



from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    d_lat = lat2 - lat1
    d_lon = lon2 - lon1

    a = sin(d_lat/2)**2 + cos(lat1) * cos(lat2) * sin(d_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c



import requests
from django.conf import settings

def get_coordinates_from_city(city_name):
    GEOAPIFY_API_KEY = settings.GEOAPIFY_API_KEY

    url = f"https://api.geoapify.com/v1/geocode/search?text={city_name}&apiKey={GEOAPIFY_API_KEY}"

    try:
        response = requests.get(url).json()
        features = response.get("features")

        if not features:
            return None, None

        coords = features[0]["geometry"]["coordinates"]
        lon, lat = coords[0], coords[1]
        return lat, lon

    except Exception as e:
        print("Geoapify Error:", e)
        return None, None


import requests
from django.conf import settings

def get_geoapify_coordinates(city):
    api_key = settings.GEOAPIFY_API_KEY
    url = f"https://api.geoapify.com/v1/geocode/search?text={city}&format=json&apiKey={api_key}"

    try:
        response = requests.get(url).json()

        if response.get("results"):
            lat = response["results"][0]["lat"]
            lon = response["results"][0]["lon"]
            return lat, lon
        return None, None

    except Exception as e:
        print("Geoapify error:", e)
        return None, None







# nightlife/services/bbox_utils.py
import math
# nightlife/services/grid_utils.py
def split_bbox_to_centers(bbox, rows=3, cols=3):
    """
    Input bbox: 'min_lon,min_lat,max_lon,max_lat'
    Output: list of (lat, lon) centers for grid tiles.
    Default 3x3 -> 9 center points.
    Increase rows/cols for denser coverage.
    """
    min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
    lon_step = (max_lon - min_lon) / cols
    lat_step = (max_lat - min_lat) / rows

    centers = []
    for r in range(rows):
        for c in range(cols):
            left = min_lon + c * lon_step
            right = left + lon_step
            bottom = min_lat + r * lat_step
            top = bottom + lat_step
            center_lon = (left + right) / 2
            center_lat = (bottom + top) / 2
            centers.append((center_lat, center_lon))
    return centers



# utils.py
from difflib import SequenceMatcher
import random
from django.core.mail import send_mail
from django.utils import timezone


def is_similar(a, b, threshold=0.6):
    """Check similarity between two strings."""
    if not a or not b:
        return False
    similarity = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    return similarity >= threshold


def generate_otp():
    """Generate a 4-digit OTP"""
    return str(random.randint(1000, 9999))


def send_approval_email(email, otp):
    send_mail(
        subject="Congratulations! Your nightclub registration has been approved. You can now log in to your account. Please note that the OTP will expire in 2 minutes.",
        message=f"Your account is approved. Your OTP is: {otp}",
        from_email="no-reply@clubapp.com",
        recipient_list=[email],
    )


def send_rejection_email(email):
    send_mail(
        subject="Your Account Has Been Rejected",
        message="Unfortunately, your registration request was rejected.",
        from_email="no-reply@clubapp.com",
        recipient_list=[email],
    )
