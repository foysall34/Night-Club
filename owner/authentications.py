# owner/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import ClubOwner  # Import your ClubOwner model










class ClubOwnerAuthentication(JWTAuthentication):
    """
    Custom authentication class for ClubOwner users.
    This class overrides the get_user method to fetch a ClubOwner instance
    instead of the default User instance.
    """
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
        except KeyError:
            return None # Token is invalid

        try:
            # The key change: We explicitly query the ClubOwner model.
            user = ClubOwner.objects.get(pk=user_id)
        except ClubOwner.DoesNotExist:
            return None # User does not exist

        return user
    

