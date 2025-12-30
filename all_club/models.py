from django.db import models
from all_club.utils import get_lat_lng_from_address


class Club(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    club_type = models.JSONField(max_length=255, blank=True , null=True , default=list)
    categories = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    hours = models.TextField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    social_media = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    user_reviews = models.TextField(null=True, blank=True , default="[]")
    instagram_url = models.URLField(null=True, blank=True)
    cover_charge = models.FloatField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    

    name_normalized = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )

    # Extra lat/lng fields
    lat_1 = models.FloatField(null=True, blank=True)
    lng_1 = models.FloatField(null=True, blank=True)


    music_preferences = models.JSONField(default=list, blank=True)
    ideal_vibes = models.JSONField(default=list, blank=True)
    crowd_atmosphere = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        # normalize name
        if self.name:
            self.name_normalized = (
                self.name.strip()
                .lower()
                .replace(" ", "")
                .replace("-", "")
            )

        # fetch lat/lng if missing
        if self.address and (self.lat is None or self.lng is None):
            lat, lng = get_lat_lng_from_address(self.address)
            if lat and lng:
                self.lat = lat
                self.lng = lng

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or "Unnamed Club"
