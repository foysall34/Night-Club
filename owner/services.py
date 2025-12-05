import os
import time
import requests
from urllib.parse import urlencode
from django.conf import settings


GOOGLE_API_KEY = getattr(settings, 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))


TEXT_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'
PHOTO_URL = 'https://maps.googleapis.com/maps/api/place/photo'


# Helper: call textsearch for "night clubs in New York City"
def fetch_nyc_nightclubs_textsearch(api_key, query='night club in New York City', page_token=None):
    params = {
    'query': query,
    'key': api_key,
    }
    if page_token:
        params['pagetoken'] = page_token


    r = requests.get(TEXT_SEARCH_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


# Helper: place details by place_id
def fetch_place_details(api_key, place_id, fields=None):
    if fields is None:
        fields = [
        'place_id', 'name', 'formatted_address', 'geometry', 'rating', 'user_ratings_total',
        'formatted_phone_number', 'international_phone_number', 'opening_hours', 'website', 'photos', 'url'
        ]
        params = {
        'place_id': place_id,
        'fields': ','.join(fields),
        'key': api_key,
        }
        r = requests.get(DETAILS_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.json()


    # Helper: build a photo url from photo_reference
def build_photo_url(api_key, photo_reference, maxwidth=800):
    params = {
    'photoreference': photo_reference,
    'maxwidth': maxwidth,
    'key': api_key,
    }
    return PHOTO_URL + '?' + urlencode(params)