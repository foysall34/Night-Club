from django.core.management.base import BaseCommand
from all_club.models import Club
from all_club.utils import get_lat_lng_from_address

class Command(BaseCommand):
    help = "Update missing latitude and longitude for clubs based on their address"

    def handle(self, *args, **kwargs):
        clubs = Club.objects.filter(lat__isnull=True) | Club.objects.filter(lng__isnull=True)

        if not clubs.exists():
            self.stdout.write(self.style.SUCCESS("All clubs already have latitude & longitude."))
            return

        updated_count = 0

        for club in clubs:
            if not club.address:
                self.stdout.write(self.style.WARNING(f"Skipping '{club.name}' (no address)."))
                continue

            lat, lng = get_lat_lng_from_address(club.address)

            if lat and lng:
                club.lat = lat
                club.lng = lng
                club.save(update_fields=["lat", "lng"])
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated: {club.name} → ({lat}, {lng})"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to fetch location for: {club.name}"))

        self.stdout.write(self.style.SUCCESS(f"\nTotal updated clubs: {updated_count}"))
