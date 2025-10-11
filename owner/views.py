
import os
import shutil
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from datetime import timedelta
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ClubOwner
from .serializers import *
# views.py

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.utils import timezone
from datetime import datetime, timedelta

from rest_framework import views, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ClubOwner
from .serializers import ClubOwnerRegistrationSerializer, OwnerVerifyOTPSerializer
from .utils import generate_otp, send_otp_email

# views.py

import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import ClubOwner
from .serializers import ClubOwnerRegistrationSerializer

class OwnerRegisterView(generics.CreateAPIView):
    """
    View for registering a new Club Owner.
    """
    serializer_class = ClubOwnerRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate and send OTP
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send OTP to user's email
        send_mail(
            'Your OTP for registration',
            f'Your OTP is: {otp}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "User registered successfully. Please check your email for OTP."},
            status=status.HTTP_201_CREATED
        )

class OwnerVerifyOTPView(APIView):
    """
    View for verifying OTP and activating the user's account.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp and timezone.now() - user.otp_created_at < timedelta(minutes=5):
            user.is_active = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            return Response({"message": "OTP verified and user activated."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

class OwnerResendOTPView(APIView):
    """
    View for resending OTP to the user's email.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        try:
            user = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate and send a new OTP
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send new OTP to user's email
        send_mail(
            'Your new OTP for registration',
            f'Your new OTP is: {otp}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "New OTP has been sent to your email."}, status=status.HTTP_200_OK)

class OwnerLoginView(APIView):
    """
    View for Club Owner login.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

      
        user = authenticate(username=email, password=password)

        if user is not None:
            if not user.is_active:
                return Response(
                    {"error": "This account is not active. Please verify your OTP."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "email": user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

class OwnerForgotPasswordView(APIView):
    """
    View for handling forgot password requests.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        try:
            user = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate and send a password reset token (you would typically use a more secure method)
        # For simplicity, we'll reuse the OTP mechanism
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send password reset OTP to user's email
        send_mail(
            'Password Reset Request',
            f'Your OTP to reset your password is: {otp}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Password reset OTP has been sent to your email."}, status=status.HTTP_200_OK)
        





# For  owner profile club

# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import ClubProfile ,ClubOwner
from .serializers import ClubProfileSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
# View for listing all clubs and creating a new one
from .authentications import ClubOwnerAuthentication
from .serializers import ClubProfileSerializer



class ClubProfileListCreateAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
      
        user_profiles = ClubProfile.objects.filter(owner=request.user)
        serializer = ClubProfileSerializer(user_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
    
        serializer = ClubProfileSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        success_data = {
            "message": "Club Profile created successfully!",
            "club_details": serializer.data
        }
        return Response(success_data, status=status.HTTP_201_CREATED)

class ClubProfileRetrieveUpdateDestroyAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk, user):
     
        try:
            return ClubProfile.objects.get(pk=pk, owner=user)
        except ClubProfile.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
  
        club_profile = self.get_object(pk, request.user)
        serializer = ClubProfileSerializer(club_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk, *args, **kwargs):
      
        club_profile = self.get_object(pk, request.user)
        serializer = ClubProfileSerializer(club_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        success_data = {
            "message": "Club Profile updated successfully!",
            "club_details": serializer.data
        }
        return Response(success_data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
    
        club_profile = self.get_object(pk, request.user)
        club_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import ClubProfile
from .serializers import ClubProfileSerializer

class ClubProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
      
        profiles = ClubProfile.objects.all()
        serializer = ClubProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
      
        serializer = ClubProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


""" Club Event & Legal Content Views """

class OwnerClubListAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
      
        clubs = ClubProfile.objects.filter(owner=request.user)
        serializer = OwnerClubSerializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventListCreateAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
   
        events = Event.objects.filter(club__owner=request.user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
    
        serializer = EventSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventRetrieveUpdateDestroyAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
     
        try:
 
            return Event.objects.get(pk=pk, club__owner=user)
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, pk, *args, **kwargs):
        event = self.get_object(pk, request.user)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def patch(self, request, pk, *args, **kwargs):
        event = self.get_object(pk, request.user)
        serializer = EventSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        event = self.get_object(pk, request.user)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from .models import LegalContent
from .serializers import LegalContentSerializer

class LegalContentView(APIView):
    """
    Retrieve a legal document (Privacy Policy or Terms of Service).
    """
    def get_document_type(self, type_slug):

        if type_slug == 'privacy-policy':
            return 'privacy_policy'
        elif type_slug == 'terms-of-service':
            return 'terms_of_service'
        return None

    def get(self, request, type_slug, format=None):
       
        content_type = self.get_document_type(type_slug)
        
        if not content_type:
            raise Http404

        try:
            document = LegalContent.objects.get(content_type=content_type)
        except LegalContent.DoesNotExist:
        
            return Response(
                {"detail": "Content not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = LegalContentSerializer(document)
        return Response(serializer.data)
    





from .authentications import ClubOwnerAuthentication 
from .serializers import WeeklyHoursSerializer
from .models import ClubProfile

class WeeklyHoursAPIView(APIView):
    authentication_classes = [ClubOwnerAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, user):
     
        profiles = ClubProfile.objects.filter(owner=user)

        if not profiles.exists():
            raise Http404("Club Profile not found for this owner.")
        

        return profiles.last()

    def get(self, request, *args, **kwargs):
        club_profile = self.get_object(request.user)
        serializer = WeeklyHoursSerializer(club_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        club_profile = self.get_object(request.user)
        serializer = WeeklyHoursSerializer(club_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        success_data = {
            "message": "Weekly hours updated successfully!",
            "weekly_hours": serializer.data['weekly_hours']
        }
        return Response(success_data, status=status.HTTP_200_OK)
    



# clubs/views.py



# write your review here views here 


#=========================================================================
#=========================================================================
#=========================================================================
"""************ For Custom User Authentication ************"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import User
from .serializers import (
    UserRegistrationSerializer, VerifyOTPSerializer, ResendOTPSerializer, UserLoginSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from .userutils  import send_otp_email
from rest_framework.permissions import IsAuthenticated




# For Password Reset
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.core.mail import send_mail
from django.conf import settings
from owner.models import User 

class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send OTP email
        send_otp_email(user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Registration successful. Please check your email for an OTP to verify your account."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class UserVerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            if user.otp != otp:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            
            # OTP expiry check (e.g., 5 minutes)
            if timezone.now() > user.otp_created_at + timedelta(minutes=5):
                return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.otp = None
            user.otp_created_at = None
            user.save()

            return Response({"message": "Account verified successfully. You can now log in."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserResendOTPAPIView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
            if user.is_active:
                return Response({"message": "This account is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            # Send a new OTP
            send_otp_email(user)
            return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = None
            user_type = None
            try:
                user_candidate = User.objects.get(email=email)

                if user_candidate.check_password(password):
                    user = user_candidate
                    user_type = 'user'
            except User.DoesNotExist:   
                pass
            if user is None:
                try:
                    owner_candidate = ClubOwner.objects.get(email=email)
       
                    if owner_candidate.check_password(password):
                        user = owner_candidate
                        user_type = 'owner'
                except ClubOwner.DoesNotExist:
                    pass
            if user is not None:
                if not user.is_active:

                    return Response({
                        "error": "Account not verified. Please verify your account with OTP."
                    }, status=status.HTTP_401_UNAUTHORIZED)

                refresh = RefreshToken.for_user(user)
                
                response_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user_type, 
                    'email': user.email,
                    'message': 'Login successful.'
                }
                return Response(response_data, status=status.HTTP_200_OK)

            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        user = request.user

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserForgotPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token_generator = PasswordResetTokenGenerator()
                uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
                token = token_generator.make_token(user)
                
                reset_link = f"http://your-frontend-domain/reset-password/{uidb64}/{token}/"
                
                # Send email
                subject = 'Password Reset Request'
                message = f'Hi {user.full_name},\n\nPlease click on the link below to reset your password:\n{reset_link}\n\nIf you did not request this, please ignore this email.'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

                return Response({'message': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                # Still return a success message to not reveal which emails are registered
                return Response({'message': 'If an account with this email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResetPasswordAPIView(APIView):
    def post(self, request, uidb64, token):
        serializer = ResetPasswordSerializer(data=request.data, context={'uidb64': uidb64, 'token': token})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



# for dummy response google api 


# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
@api_view(['POST']) 
def get_place_details(request):
    location = request.data.get('location', None) 
    city = request.data.get('city', None)      
  

    if not location or not city:
        error_message = {"error": "please provide both 'location' and 'city'."}
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    dummy_response = {
        "name": "Smuggler's Cove",
        "address": f"{location}, {city}",
        "distance": "1.5 km",
        "duration": "19 mins",
        "rating": 4.7,
        "short_description": "contemporary tiki bar with exotic cocktails & a fun, kitschy vibe.",
        "hours": "Mon-Sun: 5 PM - 2 AM",
        "vibes": "Tiki, Exotic, Fun",
        "club_type": "Bar",
        "price_range": "10$-50$",
        "latitude": 37.769,
        "longitude": -122.446,
        "website": "https://www.smugglerscovesf.com"
    }

    return Response(dummy_response, status=status.HTTP_200_OK)




from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
@api_view(['GET'])
def get_owners_clubs(request, owner_id):
    owner = get_object_or_404(ClubOwner, id=owner_id)
    clubs = ClubProfile.objects.filter(owner=owner)
    serializer = ClubProfileSerializer(clubs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




# for reviews part 


from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ClubProfile
from datetime import datetime
from django.core.files.storage import FileSystemStorage 
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser]) 
def manage_club_reviews(request, club_id):
    try:
        club = ClubProfile.objects.get(id=club_id)
    except ClubProfile.DoesNotExist:
        return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

  
    if request.method == 'GET':
        reviews_data = club.reviews
        return Response(reviews_data, status=status.HTTP_200_OK)


    elif request.method == 'POST':
        rating = request.data.get('rating')
        comment = request.data.get('comment', None) 
        image = request.FILES.get('image', None)     


        if not rating:
            return Response({"error": "rating provided"}, status=status.HTTP_400_BAD_REQUEST)

        image_url = None

        if image:
            fs = FileSystemStorage()
          
            filename = fs.save(image.name, image)

            image_url = fs.url(filename)
        

        new_review = {
            'success_msg' : 'Review added successfully',
            'rating': rating,
            'comment': comment,
            'image_url': image_url, 
            'timestamp': datetime.now().isoformat()
        }
        if not isinstance(club.reviews, list):
            club.reviews = []
    


        club.reviews.append(new_review)
        club.save()

        return Response(new_review, status=status.HTTP_201_CREATED)
    

# For user music preference 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, ClubOwner, UserProfile 

ALLOWED_MUSIC_GENRES = [
    "Hip-Hop", "Rock", "EDM", "R & B", "Pop", "Jazz", "Country"
]




@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_music_preferences(request):

    if isinstance(request.user, ClubOwner):
        return Response(
            {"error": "This endpoint is only for regular users."},
            status=status.HTTP_403_FORBIDDEN 
        )


    user_profile, created = UserProfile.objects.get_or_create(user=request.user)


    if request.method == 'GET':
        data = {
            'music_preferences': user_profile.music_preferences
        }
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        preferences = request.data.get('music_preferences')

        if not isinstance(preferences, list):
            return Response(
                {"error": "music_preferences must be a list."},
                status=status.HTTP_400_BAD_REQUEST
            )
  
        for genre in preferences:
            if genre not in ALLOWED_MUSIC_GENRES:
                return Response(
                    {"error": f"'{genre}' is not a valid music genre."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user_profile.music_preferences = preferences
        user_profile.save()

        return Response(
            {"message": "Your music preferences have been updated successfully."},
            status=status.HTTP_200_OK)


ALLOWED_VIBES = [
    "Rooftop Views", "Live Music", "High Energy", 
    "karaoke bar", "Dive bar", "Sports bar"
]

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_ideal_vibes(request):
    user_profile = request.user.profile

    if request.method == 'GET':
        return Response({'ideal_vibes': user_profile.ideal_vibes}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        vibes = request.data.get('ideal_vibes')
        if not isinstance(vibes, list):
            return Response({"error": "ideal_vibes must be a list."}, status=status.HTTP_400_BAD_REQUEST)
        
        for vibe in vibes:
            if vibe not in ALLOWED_VIBES:
                return Response({"error": f"'{vibe}' is not an allowed vibe."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.ideal_vibes = vibes
        user_profile.save()
        return Response({"message": "Your preferred vibes have been saved successfully."}, status=status.HTTP_200_OK)



ALLOWED_CROWDS = [
    "College vibes", "Young Professionals", "Upscale & Exclusive",
    "LGBTQ + Friendly", "Tourists & Travelers", "Date Night",
    "Big Group", "Neighborhood Locals"
]

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_crowd_atmosphere(request):
    user_profile = request.user.profile

    if request.method == 'GET':
        return Response({'crowd_atmosphere': user_profile.crowd_atmosphere}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        crowds = request.data.get('crowd_atmosphere')
        if not isinstance(crowds, list):
            return Response({"error": "crowd_atmosphere must be a list."}, status=status.HTTP_400_BAD_REQUEST)

        for crowd in crowds:
            if crowd not in ALLOWED_CROWDS:
                return Response({"error": f"'{crowd}' is not an allowed option."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.crowd_atmosphere = crowds
        user_profile.save()
        return Response({"message": "Your preferred crowd atmosphere has been saved successfully."}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_nights_out(request):
    user_profile = request.user.profile
    
    nights = request.data.get('nights_out')

    if nights is None:
        return Response({"error": "nights_out mandatory"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        nights_int = int(nights)
        if not (1 <= nights_int <= 7):
            raise ValueError
    except (ValueError, TypeError):
        return Response({"error": "nights_out must be a number between 1 and 7."}, status=status.HTTP_400_BAD_REQUEST)

    user_profile.nights_out = nights_int
    user_profile.save()
    return Response({"message": f"weekly nights out digit {nights_int} saved"}, status=status.HTTP_200_OK)