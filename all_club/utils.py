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
