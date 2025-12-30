# utils.py
import requests

def get_lat_lng_from_address(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }

        response = requests.get(url, params=params, headers={"User-Agent": "NightClubApp/1.0"})
        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None, None

    except Exception:
        return None, None




# utils.py
import requests

def get_lat_lng_from_address(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}

        response = requests.get(url, params=params, headers={"User-Agent": "NightClubApp/1.0"})
        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None, None

    except Exception:
        return None, None



























from openai import OpenAI
from django.conf import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_lat_lng_from_address(address: str):
    """
    Uses OpenAI (new SDK) to extract latitude & longitude from address.
    Returns (lat, lng) or (None, None)
    """

    prompt = f"""
You are a geocoding assistant.

Given the following address, return ONLY valid JSON.
Do not explain anything.

Address: "{address}"

JSON format:
{{
  "latitude": number | null,
  "longitude": number | null
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You return only JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        data = json.loads(content)

        lat = data.get("latitude")
        lng = data.get("longitude")

        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            return lat, lng

        return None, None

    except Exception as e:
        print("❌ OpenAI geocoding error:", e)
        return None, None
