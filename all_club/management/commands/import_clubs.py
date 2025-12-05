import json
import math
from django.core.management.base import BaseCommand
from all_club.models import Club

class Command(BaseCommand):
    help = "Import clubs from clubview_merged.json"

    def handle(self, *args, **kwargs):
        with open("clubview_merged.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0

        for item in data:
            # Convert NaN → None
            for k, v in item.items():
                if isinstance(v, float) and math.isnan(v):
                    item[k] = None

            Club.objects.create(
                name=item.get("name"),
                address=item.get("address"),
                categories=item.get("categories"),
                category_ids=item.get("category_ids"),
                city=item.get("city"),
                description=item.get("description"),
                distance=item.get("distance"),
                foursquare_id=item.get("foursquare_id"),
                hours=item.get("hours"),
                instagram_url=item.get("instagram_url"),
                is_nightlife=item.get("is_nightlife"),
                last_fsq_refresh=item.get("last_fsq_refresh"),
                lat=item.get("lat"),
                lng=item.get("lng"),
                place_id=item.get("place_id"),
                popularity=item.get("popularity"),
                price_level=item.get("price_level"),
                rating=item.get("rating"),
                social_media=item.get("social_media"),
                state=item.get("state"),
                summary=item.get("summary"),
                tips=item.get("tips"),
                types=item.get("types"),
                website=item.get("website"),
                lat_1=item.get("lat.1"),
                lng_1=item.get("lng.1"),
            )

            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} clubs!"))
