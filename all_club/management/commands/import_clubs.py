from django.core.management.base import BaseCommand
from all_club.models import Club
from all_club.utils import get_lat_lng_from_address


class Command(BaseCommand):
    help = "Update missing latitude and longitude for clubs using OpenAI geocoding"

    def handle(self, *args, **kwargs):
        clubs = Club.objects.filter(lat__isnull=True) | Club.objects.filter(lng__isnull=True)

        if not clubs.exists():
            self.stdout.write(
                self.style.SUCCESS("All clubs already have latitude & longitude.")
            )
            return

        updated_count = 0

        for club in clubs:
            self.stdout.write(f"\n📍 Processing club: {club.name}")

            if not club.address:
                self.stdout.write(
                    self.style.WARNING("⚠ Skipping (no address).")
                )
                continue

            lat, lng = get_lat_lng_from_address(club.address)

            if lat and lng:
                club.lat = lat
                club.lng = lng
                club.save(update_fields=["lat", "lng"])
                updated_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Updated → ({lat}, {lng})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "❌ Failed to fetch location from OpenAI"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Total updated clubs: {updated_count}"
            )
        )
