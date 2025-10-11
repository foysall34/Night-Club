from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import ClubOwner

# আমরা ডিফল্ট User মডেলটি পাব AUTH_USER_MODEL সেটিং থেকে
User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
    
        email = username

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
      
            try:
                user = ClubOwner.objects.get(email=email)
                if user.check_password(password):
                    return user
            except ClubOwner.DoesNotExist:
           
                return None
        return None

    def get_user(self, user_id):
  
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
      
            try:
                return ClubOwner.objects.get(pk=user_id)
            except ClubOwner.DoesNotExist:
                return None