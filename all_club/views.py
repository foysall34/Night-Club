from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Club


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])   # 🔐 TOKEN REQUIRED
def club_details(request, club_id):
    """
    GET  -> Club details
    PATCH -> Update club (e.g. is_favorite)
    """

    try:
        club = Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        return Response(
            {"error": "Club not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # =========================
    # GET: Club Details
    # =========================
    if request.method == "GET":
        data = {
            "id": club.id,
            "name": club.name,
            "address": club.address,
            "city": club.city,
            "club_type": club.club_type,
            "categories": club.categories,
            "description": club.description,
            "hours": club.hours,
            "rating": club.rating,
            "lat": club.lat,
            "lng": club.lng,
            "instagram_url": club.instagram_url,
            "website": club.website,
            "photo_url": club.photo_url,
            "is_favorite": club.is_favorite,
            "user_reviews": club.user_reviews,
            "music_preferences": club.music_preferences,
            "ideal_vibes": club.ideal_vibes,
            "crowd_atmosphere": club.crowd_atmosphere,
        }
        return Response(data, status=status.HTTP_200_OK)

    # =========================
    # PATCH: Partial Update
    # =========================
    if request.method == "PATCH":

        # Only allow safe fields
        allowed_fields = ["is_favorite"]

        updated = False
        for field in allowed_fields:
            if field in request.data:
                setattr(club, field, request.data.get(field))
                updated = True

        if not updated:
            return Response(
                {"error": "No valid fields to update"},
                status=status.HTTP_400_BAD_REQUEST
            )

        club.save(update_fields=allowed_fields)

        return Response({
            "message": "Club updated successfully",
            "id": club.id,
            "is_favorite": club.is_favorite
        }, status=status.HTTP_200_OK)
