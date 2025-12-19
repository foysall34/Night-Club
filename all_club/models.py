
from django.db import models

from all_club.utils import get_lat_lng_from_address

class Club(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    categories = models.TextField(null=True, blank=True)
    category_ids = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    foursquare_id = models.CharField(max_length=255, null=True, blank=True)
    hours = models.TextField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)
    is_nightlife = models.BooleanField(null=True, blank=True)
    last_fsq_refresh = models.CharField(max_length=255, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    place_id = models.CharField(max_length=255, null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    social_media = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    tips = models.TextField(null=True, blank=True)
    types = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)
    name_normalized = models.CharField(
        max_length=255,
        unique=True,
        db_index=True , null=True, blank=True
    )

    # Extra lat/lng fields
    lat_1 = models.FloatField(null=True, blank=True)
    lng_1 = models.FloatField(null=True, blank=True)


    

    def save(self, *args, **kwargs):
        if self.name:
            self.name_normalized = (
                self.name.strip().lower()
                .replace(" ", "")
                .replace("-", "")
            )
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # If address exists and lat/lng empty → fetch from API
        if self.address and (self.lat is None or self.lng is None):
            lat, lng = get_lat_lng_from_address(self.address)
            if lat and lng:
                self.lat = lat
                self.lng = lng

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or "Unnamed Club"
