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
import os
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
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import ClubOwner
from .serializers import ClubOwnerRegistrationSerializer ,ClubOwnerStatusSerializer



@api_view(['GET'])
def get_all_clubowners_status(request):
    owners = ClubOwner.objects.all().order_by('-id')  
    serializer = ClubOwnerStatusSerializer(owners, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




class OwnerRegisterView(generics.CreateAPIView):
    serializer_class = ClubOwnerRegistrationSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()     
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        send_mail(
            'Your OTP for registration',
            f'Your OTP is: {otp}',
            'from@example.com',
            [user.email],
            fail_silently=False,)
        return Response(
            {"message": "User registered successfully. Please check your email for OTP."},
            status=status.HTTP_201_CREATED)

class OwnerVerifyOTPView(APIView):
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

        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

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

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
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

        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        send_mail(
            'Password Reset Request',
            f'Your OTP to reset your password is: {otp}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Password reset OTP has been sent to your email."}, status=status.HTTP_200_OK)
        


class OwnerPasswordResetView(APIView):
    """
    View for resetting the user's password using an OTP.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        # otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        # password_confirmation = request.data.get('password_confirmation')


        # if not all([email, otp, new_password, password_confirmation]):
        #     return Response({"error": "Please provide email, OTP, and new password."}, status=status.HTTP_400_BAD_REQUEST)


        # if new_password != password_confirmation:
        #     return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:

            user = ClubOwner.objects.get(email=email)  
            # if user.otp != otp:
            #     return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


            # if user.otp_created_at:
            #     otp_expiry_time = user.otp_created_at + timedelta(minutes=10)
            #     if timezone.now() > otp_expiry_time:
            
            #         user.otp = None
            #         user.otp_created_at = None
            #         user.save()
            #         return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
            # else:
            #      return Response({"error": "No OTP was requested."}, status=status.HTTP_400_BAD_REQUEST)



            user.set_password(new_password)

     
            # user.otp = None
            # user.otp_created_at = None
            user.save()

            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        except ClubOwner.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)




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
from rest_framework.decorators import api_view 



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



from .models import ClubType, Vibes_Choice
from .serializers import ClubTypeSerializer, VibesChoiceSerializer

class ClubTypeListAPIView(generics.ListAPIView):
   
    queryset = ClubType.objects.all()
    serializer_class = ClubTypeSerializer
   

class VibesChoiceListAPIView(generics.ListAPIView):
  
    queryset = Vibes_Choice.objects.all()
    serializer_class = VibesChoiceSerializer
   








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


@api_view(['GET'])
def get_all_events(request):
    events = Event.objects.all().order_by('-date', '-time')
    serializer = Get_all_EventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_upcoming_events(request):
    today = timezone.now().date()
    events = Event.objects.filter(created_at__date__gte=today).order_by('date', 'time')


    serializer = Get_all_EventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

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






#=========================================================================
#=========================================================================
"""************ For Custom User Authentication ************"""
#=========================================================================
#=========================================================================

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
    ChangePasswordSerializer, 
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
            
            # if user.is_active:
            #     return Response({"message": "This account is already verified."}, status=status.HTTP_400_BAD_REQUEST)

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
        serializer = ForgotPasswordOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                send_otp_email(user)
            except User.DoesNotExist:
           
                pass
            return Response({'message': 'If your email is registered, an OTP has been sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordWithOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'Invalid email or OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            # OTP match & time check
            # if user.otp != otp:
            #     return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            # if user.otp_created_at + timedelta(minutes=5) < timezone.now():
            #     return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)

            # Password reset
            user.set_password(new_password)
            # user.otp = None
            # user.otp_created_at = None
            user.save()

            return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# for dummy response google api 


# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
@api_view(['POST'])
def get_place_details(request):
    email = request.data.get('email')
    location = request.data.get('location')
    city = request.data.get('city')

  
    if not email:
        return Response({"error": "email field is required."}, status=status.HTTP_400_BAD_REQUEST)


    if not location and not city:
        return Response(
            {"error": "please provide either 'location' or 'city'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    
    final_location = location if location else city

    dummy_response = {
        "email": email,
        "name": "Smuggler's Cove",
        "address": f"{final_location}",
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





# all club by get 


@api_view(['GET'])
def get_all_clubs(request):
    clubs = ClubProfile.objects.all()
    data = []

    for club in clubs:

        reviews_data = club.reviews if isinstance(club.reviews, list) else []

        if reviews_data:
            total_rating = sum(float(r['rating']) for r in reviews_data if 'rating' in r)
            avg_rating = round(total_rating / len(reviews_data), 1)
        else:
            avg_rating = 0.0

        data.append({
            "id": club.id,
            "owner": club.owner.full_name if club.owner else None,
            "clubName": club.clubName,
            "club_type": [ct.name for ct in club.club_type.all()],
            "vibes_type": [v.name for v in club.vibes_type.all()],
            "clubImageUrl": club.clubImageUrl.url if club.clubImageUrl else None,
            "features": club.features,
            "events": club.events,
            "crowd_atmosphere": club.crowd_atmosphere,
            "is_favourite": club.is_favourite,

            "average_rating": avg_rating,
            "total_reviews": len(reviews_data),
        })

    return Response({"clubs": data}, status=status.HTTP_200_OK)


# Filter by club type 


def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to calculate distance in km between two points"""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

@api_view(['POST'])
def get_clubs_by_type_post(request):
    club_type_name = request.data.get('club_type')
    email = request.data.get('email')
    debug_logs = []

    if not email:
        return Response({"error": "email is required"}, status=400)

    try:
        user_profile = UserProfile.objects.get(user__email=email)
        user_lat, user_lon = float(user_profile.latitude), float(user_profile.longitude)
        debug_logs.append(f"User location: lat={user_lat}, lon={user_lon}")
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=404)


    if club_type_name:
        clubs = ClubProfile.objects.filter(club_type__name=club_type_name)
    else:
        clubs = ClubProfile.objects.all()

 
    data = []
    for club in clubs:
        if club.latitude is not None and club.longitude is not None:
            distance = calculate_distance(user_lat, user_lon, float(club.latitude), float(club.longitude))
            debug_logs.append(f"Club: {club.clubName}, location: ({club.latitude}, {club.longitude}), distance={distance:.2f} km")
            data.append({
                "id": club.id,
                "distance_km": round(distance, 2)
            })

    return Response({"clubs": data}, status=200)





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

    # ================= GET REQUEST =================
    if request.method == 'GET':
        reviews_data = club.reviews if isinstance(club.reviews, list) else []
        

        if reviews_data:
            total_rating = sum(float(r['rating']) for r in reviews_data if 'rating' in r)
            avg_rating = round(total_rating / len(reviews_data), 1)
        else:
            avg_rating = 0.0
        
        return Response({
            "average_rating": avg_rating,
            "total_reviews": len(reviews_data),
            "reviews": reviews_data
        }, status=status.HTTP_200_OK)

    # ================= POST REQUEST =================
    elif request.method == 'POST':
        rating = request.data.get('rating')
        comment = request.data.get('comment', None)
        image = request.FILES.get('image', None)

        if not rating:
            return Response({"error": "Rating is required"}, status=status.HTTP_400_BAD_REQUEST)

        image_url = None
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_url = fs.url(filename)

        new_review = {
            'rating': float(rating),
            'comment': comment,
            'image_url': image_url,
            'timestamp': datetime.now().isoformat()
        }

        if not isinstance(club.reviews, list):
            club.reviews = []

        club.reviews.append(new_review)
        club.save()

        total_rating = sum(float(r['rating']) for r in club.reviews)
        avg_rating = round(total_rating / len(club.reviews), 1)

        return Response({
            "success_msg": "Review added successfully",
            "new_review": new_review,
            "average_rating": avg_rating,
            "total_reviews": len(club.reviews)
        }, status=status.HTTP_201_CREATED)









# For user music preference 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, ClubOwner, UserProfile , MusicGenre , Vibe ,CrowdAtmosphere

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import User, UserProfile, MusicGenre, Vibe, CrowdAtmosphere

@api_view(['GET', 'POST', 'PATCH'])
def manage_user_profile_preferences(request):

    email = request.data.get('email') or request.query_params.get('email')
    if not email:
        return Response({"error": "email field is required."}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, email=email)
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    # =============================
    #   GET Method
    # =============================
    if request.method == 'GET':
        music = list(user_profile.music_preferences.values_list('name', flat=True))
        vibes = list(user_profile.ideal_vibes.values_list('name', flat=True))
        crowds = list(user_profile.crowd_atmosphere.values_list('name', flat=True))
        nights = user_profile.nights_out if hasattr(user_profile, 'nights_out') else None

        return Response({
            "email": email,
            "music_preferences": music,
            "vibes": vibes,
            "crowd_atmosphere": crowds,
            "nights_out": nights
        }, status=status.HTTP_200_OK)

    # =============================
    # POST Method 
    # =============================
    elif request.method == 'POST':
        #  Music
        music_names = request.data.get('music_preferences', [])
        if not isinstance(music_names, list):
            return Response({"error": "music_preferences must be a list."}, status=status.HTTP_400_BAD_REQUEST)
        valid_music = MusicGenre.objects.filter(name__in=music_names)
        user_profile.music_preferences.set(valid_music)

        #  Vibe
        vibe_names = request.data.get('vibes', [])
        if not isinstance(vibe_names, list):
            return Response({"error": "vibes must be a list."}, status=status.HTTP_400_BAD_REQUEST)
        valid_vibes = Vibe.objects.filter(name__in=vibe_names)
        user_profile.ideal_vibes.set(valid_vibes)

        # Crowd Atmosphere
        crowd_names = request.data.get('crowd_atmosphere', [])
        if not isinstance(crowd_names, list):
            return Response({"error": "crowd_atmosphere must be a list."}, status=status.HTTP_400_BAD_REQUEST)
        valid_crowds = CrowdAtmosphere.objects.filter(name__in=crowd_names)
        user_profile.crowd_atmosphere.set(valid_crowds)

        #  Nights out
        nights = request.data.get('nights_out')
        if nights is not None:
            try:
                nights_int = int(nights)
                if not (1 <= nights_int <= 7):
                    raise ValueError
                user_profile.nights_out = nights_int
            except (ValueError, TypeError):
                return Response({"error": "nights_out must be a number between 1 and 7."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.save()

        return Response({"message": "All preferences set successfully."}, status=status.HTTP_200_OK)

    # =============================
    # 🛠 PATCH Method (Update / Add)
    # =============================
    elif request.method == 'PATCH':
        # Music
        music_names = request.data.get('music_preferences', [])
        if isinstance(music_names, list):
            current_music = set(user_profile.music_preferences.values_list('name', flat=True))
            updated_music = current_music.union(set(music_names))
            valid_music = MusicGenre.objects.filter(name__in=updated_music)
            user_profile.music_preferences.set(valid_music)

        #  Vibe
        vibe_names = request.data.get('vibes', [])
        if isinstance(vibe_names, list):
            current_vibes = set(user_profile.ideal_vibes.values_list('name', flat=True))
            updated_vibes = current_vibes.union(set(vibe_names))
            valid_vibes = Vibe.objects.filter(name__in=updated_vibes)
            user_profile.ideal_vibes.set(valid_vibes)

        #  Crowd
        crowd_names = request.data.get('crowd_atmosphere', [])
        if isinstance(crowd_names, list):
            current_crowds = set(user_profile.crowd_atmosphere.values_list('name', flat=True))
            updated_crowds = current_crowds.union(set(crowd_names))
            valid_crowds = CrowdAtmosphere.objects.filter(name__in=updated_crowds)
            user_profile.crowd_atmosphere.set(valid_crowds)

        nights = request.data.get('nights_out')
        if nights is not None:
            try:
                nights_int = int(nights)
                if not (1 <= nights_int <= 7):
                    raise ValueError
                user_profile.nights_out = nights_int
            except (ValueError, TypeError):
                return Response({"error": "nights_out must be a number between 1 and 7."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile.save()

        return Response({"message": "Preferences updated successfully."}, status=status.HTTP_200_OK)






















#=========================================================================
# for follow & followres 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserFollowSerializer

class FollowToggleView(APIView):
 
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id, *args, **kwargs):
        user_to_toggle = get_object_or_404(User, id=user_id)
        current_user = request.user

        if user_to_toggle == current_user:
            return Response({'error': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

  
        if current_user.following.filter(id=user_to_toggle.id).exists():
            current_user.following.remove(user_to_toggle)
            message = f'You have unfollowed {user_to_toggle.full_name}.'
            return Response({'message': message, 'action': 'unfollowed'}, status=status.HTTP_200_OK)
    
        else:
            current_user.following.add(user_to_toggle)
            message = f'You are now following {user_to_toggle.full_name}.'
            return Response({'message': message, 'action': 'followed'}, status=status.HTTP_200_OK)


class FollowingPageView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        current_user = request.user
        following_users = current_user.following.all()
        my_follower_ids = current_user.followers.values_list('id', flat=True)
        my_following_ids = current_user.following.values_list('id', flat=True)

        follow_back_users = User.objects.filter(id__in=my_follower_ids).exclude(id__in=my_following_ids)

     
        exclude_ids = list(my_following_ids) + list(follow_back_users.values_list('id', flat=True)) + [current_user.id]
        other_suggestions = User.objects.exclude(id__in=exclude_ids)[:10]

       
        suggested_users = list(follow_back_users) + list(other_suggestions)

        serializer_context = {'request': request}
        following_serializer = UserFollowSerializer(following_users, many=True, context=serializer_context)
        suggestions_serializer = UserFollowSerializer(suggested_users, many=True, context=serializer_context)

        response_data = {
            'following': following_serializer.data,
            'suggestions': suggestions_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    





# For Recomendation veiws 


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        import json
        print(json.dumps(serializer.data, indent=4))
        return Response(serializer.data)
    


from rest_framework import generics, permissions
from .models import ClubProfile
from .serializers import ClubDetailSerializer
import json
class ClubDetailView(generics.RetrieveAPIView):
  
    queryset = ClubProfile.objects.select_related('owner').all()
    serializer_class = ClubDetailSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
      
     
        instance = self.get_object() 
        
        
        serializer = self.get_serializer(instance)
        
 
        print("--- Club Detail Data ---")

        print(json.dumps(serializer.data, indent=4))
        print("------------------------")
      

  
        return Response(serializer.data)
    

#************************************************************************************************
# Final Recommedation api 
#************************************************************************************************

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from owner.models import ClubProfile, UserProfile
from owner.serializers import ClubProfileSerializer
from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_clubs(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)

    try:
        user_lat = float(profile.latitude)
        user_lon = float(profile.longitude)
    except (TypeError, ValueError):
        return Response({"error": "User location missing"}, status=400)

 
    user_music = set([str(x) for x in profile.music_preferences.all()])
    user_vibes = set([str(x) for x in profile.ideal_vibes.all()])
    user_crowd = set([str(x) for x in profile.crowd_atmosphere.all()])

    clubs = ClubProfile.objects.select_related('owner').all()
    recommendations = []

    for club in clubs:
        owner = club.owner
        if not owner or owner.latitude is None or owner.longitude is None:
            continue

        distance = calculate_distance(user_lat, user_lon, float(owner.latitude), float(owner.longitude))
        if distance > 30:
            continue  

     
        club_music = set(club.features.get('music_preferences', []))
        club_vibes = set(club.events.get('ideal_vibes', []))
        club_crowd = set(club.crowd_atmosphere.get('crowd&atmosphere', []))


        music_match = len(user_music.intersection(club_music))
        vibes_match = len(user_vibes.intersection(club_vibes))
        crowd_match = len(user_crowd.intersection(club_crowd))

        total_match = music_match + vibes_match + crowd_match

        if total_match > 0:
            recommendations.append({
                "id": club.id,
         
            })

    sorted_recommendations = sorted(recommendations, key=lambda x: (-x['total_match'], x['distance_km']))

    return Response({
        "count": len(sorted_recommendations),
        "results": sorted_recommendations[:5]  
    })

# Best club id suggestion 

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_recommended_club(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)

    try:
        user_lat = float(profile.latitude)
        user_lon = float(profile.longitude)
    except (TypeError, ValueError):
        return Response({"error": "User location missing"}, status=400)


    user_music = set(str(x) for x in profile.music_preferences.all())
    user_vibes = set(str(x) for x in profile.ideal_vibes.all())
    user_crowd = set(str(x) for x in profile.crowd_atmosphere.all())

    clubs = ClubProfile.objects.select_related('owner').all()
    recommendations = []

    for club in clubs:
        owner = club.owner
        if not owner or owner.latitude is None or owner.longitude is None:
            continue

        distance = calculate_distance(user_lat, user_lon, float(owner.latitude), float(owner.longitude))
        if distance > 30:
            continue

        club_music = set(club.features.get('music_preferences', []))
        club_vibes = set(club.events.get('ideal_vibes', []))
        club_crowd = set(club.crowd_atmosphere.get('crowd&atmosphere', []))

        music_match = len(user_music.intersection(club_music))
        vibes_match = len(user_vibes.intersection(club_vibes))
        crowd_match = len(user_crowd.intersection(club_crowd))

        total_match = music_match + vibes_match + crowd_match

        if total_match > 0:
            recommendations.append({
                "id": club.id,
                "total_match": total_match,
                "distance_km": round(distance, 2)
            })

    if not recommendations:
        return Response({"message": "No recommended club found"}, status=404)

    top_club = sorted(recommendations, key=lambda x: (-x['total_match'], x['distance_km']))[0]

    return Response({
        "top_recommended_club_id": top_club["id"],
        "match_score": top_club["total_match"],
        "distance_km": top_club["distance_km"]
    })

# for Trending Club 

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

@api_view(['POST'])
def club_click(request, club_id):
    club = get_object_or_404(ClubProfile, id=club_id)
    club.click_count += 1
    club.save()
    return Response({"message": f"{club.clubName} clicked", "total_clicks": club.click_count}, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_trendy_club(request, owner_id):
    owner = get_object_or_404(ClubOwner, id=owner_id)
    trendy_club_ids = ClubProfile.objects.filter(owner=owner).order_by('-click_count').values_list('id', flat=True)

    if not trendy_club_ids.exists():
        return Response({"message": "No clubs found for this owner"}, status=status.HTTP_404_NOT_FOUND)

    return Response({"club_ids": list(trendy_club_ids)}, status=status.HTTP_200_OK)





class DashboardStatsView(APIView):
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        dummy_data = {
            "events_this_month": {
                "value": 7,
                "comparison": "3 more than last month"
            },
            "live_events": {
                "title": " Night",
                "viewers": 325
            },
            "reviews": {
                "rating": 4.5,
                "count": 86,
                "period": "this week"
            },
            "revenue": {
                "amount": 600,
                "percentage_change": 15,
                "comparison": "vs last month"
            }
        }
        return Response(dummy_data)
    


class AnalyticalDashboard(APIView):
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        dummy_data = {
            "Total Events Created": {
                "value": 5,
            },
            "Profile Views": {
 
                "viewers": 3
            },
            "Total Attendees": {
        
                "count": 86,
                
            },
            "Engagement Rate": {
                "Rate":"4.2%"
               
            }
        }
        return Response(dummy_data)
    



# nearby clubs 

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from math import radians, sin, cos, sqrt, atan2

from .models import ClubProfile, UserProfile

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Haversine formula to calculate distance in km between two points
    """
    R = 6371  
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

@api_view(['GET', 'POST'])
def nearby_clubs(request):
    """
    Returns clubs within 5 km of user
    Debug version included
    """
    email = request.data.get('email') or request.query_params.get('email')
    if not email:
        return Response({"error": "email field is required"}, status=status.HTTP_400_BAD_REQUEST)

    debug_logs = []

 
    try:
        user_profile = UserProfile.objects.get(user__email=email)
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    debug_logs.append(f"User email: {email}")
    debug_logs.append(f"User location: lat={user_profile.latitude}, lon={user_profile.longitude}")

    if not user_profile.latitude or not user_profile.longitude:
        return Response({"error": "User location not set", "debug_logs": debug_logs}, status=status.HTTP_400_BAD_REQUEST)

    nearby = []
    for club in ClubProfile.objects.all():
        if club.latitude is not None and club.longitude is not None:
            distance = calculate_distance(
                float(user_profile.latitude), 
                float(user_profile.longitude),
                float(club.latitude),
                float(club.longitude)
            )
            debug_logs.append(f"Club: {club.clubName}, location: ({club.latitude}, {club.longitude}), distance={distance:.2f} km")
            if distance <= 5: 
                nearby.append({
                    "id": club.id,
                    "distance_km": round(distance, 2),
               
                })

    return Response({"nearby_clubs": nearby, "debug_logs": debug_logs}, status=status.HTTP_200_OK)



# Open today 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, time
from .models import ClubProfile, UserProfile
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula for distance in km"""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    return R*c

@api_view(['POST'])
def nearby_currently_open_clubs(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "email field is required"}, status=400)

    debug_logs = []

    try:
        user_profile = UserProfile.objects.get(user__email=email)
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if not user_profile.latitude or not user_profile.longitude:
        return Response({"error": "User location not set"}, status=400)

    debug_logs.append(f"User location: lat={user_profile.latitude}, lon={user_profile.longitude}")

    today = datetime.now().strftime("%A").lower()  
    now_time = datetime.now().time()

    nearby = []

    for club in ClubProfile.objects.all():
        if club.latitude is None or club.longitude is None:
            debug_logs.append(f"Club {club.clubName} has no location")
            continue

        distance = calculate_distance(
            float(user_profile.latitude),
            float(user_profile.longitude),
            float(club.latitude),
            float(club.longitude)
        )
        debug_logs.append(f"Club: {club.clubName}, distance={distance:.2f} km")

        if distance > 5:
            continue 

        weekly_hours = club.weekly_hours or {}
        today_hours = weekly_hours.get(today)
        if not today_hours:
            debug_logs.append(f"Club {club.clubName} has no hours for today")
            continue

        start_str = today_hours.get('start_time')
        end_str = today_hours.get('end_time')
        if not start_str or not end_str:
            debug_logs.append(f"Club {club.clubName} start/end time missing for today")
            continue

        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()

       
        if start_time < end_time:
            is_open = start_time <= now_time <= end_time
        else:

            is_open = now_time >= start_time or now_time <= end_time

        if is_open:
            nearby.append({
                "id": club.id,

         
           
                "distance_km": round(distance, 2),
  
            })
        else:
            debug_logs.append(f"Club {club.clubName} is closed now")

    if not nearby:
        return Response({"message": "No club is open now", "debug_logs": debug_logs}, status=200)

    return Response({"nearby_open_clubs": nearby, "debug_logs": debug_logs}, status=200)




# is favourite 

@api_view(['GET', 'PATCH'])
def favourite_clubs(request):
   
    if request.method == 'PATCH':
        club_id = request.data.get('club_id')
        is_fav = request.data.get('is_favourite')

        if club_id is None or is_fav is None:
            return Response({"error": "club_id and is_favourite are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            club = ClubProfile.objects.get(id=club_id)
        except ClubProfile.DoesNotExist:
            return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(is_fav, str):
            is_fav = is_fav.lower() in ['true', '1', 'yes']

        club.is_favourite = bool(is_fav)
        club.save()

        return Response({"message": f"Club '{club.clubName}' favourite status updated to {club.is_favourite}"}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        favourite_clubs = ClubProfile.objects.filter(is_favourite=True)
        data = []
        for club in favourite_clubs:
            data.append({
                "id": club.id,
                "clubName": club.clubName,
                "club_location": club.club_location,
                "latitude": club.latitude,
                "longitude": club.longitude,
                "is_favourite": club.is_favourite,
                "phone": club.phone,
                "email": club.email,
            })
        return Response({"favourite_clubs": data}, status=status.HTTP_200_OK)
    


# Edit user profile 
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):

    user = request.user

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    # --- Update User full_name ---
    full_name = request.data.get('full_name')
    if full_name is not None:
        user.full_name = full_name
        user.save(update_fields=['full_name'])

    # --- Update City ---
    city = request.data.get('city')
    if city is not None:
        profile.city = city

    # --- Update About ---
    about = request.data.get('about')
    if about is not None:
        profile.about = about

    # --- Update Music Preferences ---
    music_ids = request.data.get('music_preferences')
    if music_ids is not None:
        if not isinstance(music_ids, list):
            return Response({"error": "music_preferences must be a list of IDs"}, status=status.HTTP_400_BAD_REQUEST)
        genres = MusicGenre.objects.filter(id__in=music_ids)
        profile.music_preferences.set(genres)

    profile.save()

    return Response({
        "message": "Profile updated successfully ",
        "Review" : 2 ,
        "Followers" : 5 , 
        "Following" : 3  , 
        "full_name": user.full_name,
        "city": profile.city,
        "about": profile.about,
        "music_preferences": list(profile.music_preferences.values_list('name', flat=True))
    }, status=status.HTTP_200_OK)