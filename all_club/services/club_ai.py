from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def filter_allowed(ai_list, allowed_list):
    if not isinstance(ai_list, list):
        return []
    return [item for item in ai_list if item in allowed_list]



# all_club/constants.py

CLUB_TYPES = [
    "EDM",
    "Nightclub",
    "Lounge",
    "Bar",
    "Live Music",
    "Rooftop",
    "Mixed"
]



MUSIC_PREFERENCES = [
    "Hip-Hop",
    "Rock",
    "EDM",
    "R&B",
    "Pop",
    "Jazz",
    "Country"
]

IDEAL_VIBES = [
    "Rooftop Views",
    "Live Music",
    "High Energy",
    "Karaoke Bar",
    "Dive Bar",
    "Sports Bar"
]

CROWD_ATMOSPHERE = [
    "College Vibes",
    "Young Professionals",
    "Upscale & Exclusive",
    "LGBTQ+ Friendly",
    "Tourists & Travelers",
    "Date Night",
    "Big Group",
    "Neighborhood Locals"
]




from openai import OpenAI
from django.conf import settings

import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def enrich_club_with_ai(club):
    prompt = f"""
You are categorizing a nightlife club.

Club Name: {club.name}
City: {club.city}
Description: {club.description}

STRICT RULES:
- Choose ONLY from the provided lists
- Choose 1–3 items per category
- Do NOT invent values
- Return ONLY valid JSON

Music Preferences:
{", ".join(MUSIC_PREFERENCES)}

Ideal Vibes:
{", ".join(IDEAL_VIBES)}

Crowd Atmosphere:
{", ".join(CROWD_ATMOSPHERE)}

JSON FORMAT:
{{
  "music_preferences": [],
  "ideal_vibes": [],
  "crowd_atmosphere": []
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    return json.loads(content)