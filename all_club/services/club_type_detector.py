import re
from datetime import datetime


def detect_from_categories(categories):
    if not categories:
        return None

    text = categories.lower()

    if any(x in text for x in ["edm", "dj", "techno", "house"]):
        return "EDM"
    if any(x in text for x in ["lounge", "chill", "cocktail"]):
        return "Lounge"
    if any(x in text for x in ["bar", "pub", "tavern"]):
        return "Bar"
    if any(x in text for x in ["nightclub", "dance club", "club"]):
        return "Nightclub"
    if any(x in text for x in ["live", "band", "concert"]):
        return "Live Music"
    if "rooftop" in text:
        return "Rooftop"

    return None


def detect_from_hours(hours):
    """
    Example hours:
    '18:00-02:00'
    '5 PM – 3 AM'
    """
    if not hours:
        return None

    hours = hours.lower()

    # Nightclub heuristic
    if any(x in hours for x in ["2 am", "3 am", "4 am", "late"]):
        return "Nightclub"

    # Bar heuristic
    if any(x in hours for x in ["12 am", "midnight"]):
        return "Bar"

    # Lounge heuristic
    if any(x in hours for x in ["evening", "sunset"]):
        return "Lounge"

    return None
