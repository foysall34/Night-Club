from django.core.management.base import BaseCommand
from all_club.models import Club
from all_club.services.club_ai import enrich_club_with_ai
from all_club.services.club_type_detector import (
    detect_from_categories,
    detect_from_hours
)


class Command(BaseCommand):
    help = "Detect club_type using categories → hours → OpenAI fallback"

    def handle(self, *args, **kwargs):
        clubs = Club.objects.all()

        for club in clubs:
            try:
                self.stdout.write(f"\n🔍 Processing: {club.name}")

                club_type = None

                # -------------------------
                # 1️⃣ Categories based
                # -------------------------
                club_type = detect_from_categories(club.categories)
                if club_type:
                    self.stdout.write(f"✔ From categories: {club_type}")

                # -------------------------
                # 2️⃣ Hours based fallback
                # -------------------------
                if not club_type:
                    club_type = detect_from_hours(club.hours)
                    if club_type:
                        self.stdout.write(f"✔ From hours: {club_type}")

                # -------------------------
                # 3️⃣ OpenAI fallback (last)
                # -------------------------
                if not club_type:
                    self.stdout.write("🤖 Using OpenAI fallback")
                    ai_data = enrich_club_with_ai(club)
                    club_type = ai_data.get("club_type", "Mixed")

                club.club_type = [club_type]
                club.save(update_fields=["club_type"])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Final club_type: {club.club_type}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Failed {club.name}: {str(e)}"
                    )
                )
