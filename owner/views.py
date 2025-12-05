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
from .utils import generate_otp, get_coordinates_from_city, send_otp_email
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
from .serializers import ClubProfileSerializer , MyClubProfileSerializer
from rest_framework.decorators import api_view 

class ClubProfileByEmailView(APIView):
    """
    View to handle ClubProfile fetch and update by owner's email.
    Supports GET, POST, and PATCH requests.
    """

    def get(self, request):
        """
        GET: Retrieve club profile by owner's email via query parameter
        Example: /api/club-profile-by-email/?email=example@gmail.com
        """
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Email is required as a query parameter."},
                            status=status.HTTP_400_BAD_REQUEST)

        owner = get_object_or_404(ClubOwner, email=email)
        profile = get_object_or_404(ClubProfile, owner=owner)
        serializer = MyClubProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        POST: Get club profile by owner's email (from request body)
        """
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        owner = get_object_or_404(ClubOwner, email=email)
        profile = get_object_or_404(ClubProfile, owner=owner)
        serializer = MyClubProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        PATCH: Update club profile by owner's email.
        Accepts multiple IDs for club_type and vibes_type.
        Example JSON:
        {
          "email": "owner@example.com",
          "club_type": [1, 2, 3],
          "vibes_type": [4, 5],
          "venue_name": "New Club Name"
        }
        """
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        owner = get_object_or_404(ClubOwner, email=email)
        profile = get_object_or_404(ClubProfile, owner=owner)

        # Pop ManyToMany fields from request safely
        club_type_ids = request.data.pop('club_type', None)
        vibes_type_ids = request.data.pop('vibes_type', None)

        # Update normal fields first
        serializer = MyClubProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update ManyToMany fields separately
        if club_type_ids is not None:
            profile.club_type.set(ClubType.objects.filter(id__in=club_type_ids))
        if vibes_type_ids is not None:
            profile.vibes_type.set(Vibes_Choice.objects.filter(id__in=vibes_type_ids))

        profile.save()

        # Return updated data
        updated_serializer = MyClubProfileSerializer(profile)
        return Response(
            {
                "message": "Club profile updated successfully.",
                "data": updated_serializer.data,
            },
            status=status.HTTP_200_OK
        )






class EventsByOwnerEmailView(APIView):
    """
    Handle events related to a specific ClubOwner using their email.
    
    POST:
      - If only 'email' is provided: returns all events for that owner.
      - If 'email' + event details are provided: creates a new event.

    GET:
      - ?email=<email> → returns all events for the owner
      - ?email=<email>&event_id=<id> → returns single event

    PATCH:
      - Partial update an event using 'email' + 'event_id'

    DELETE:
      - Delete an event using 'email' + 'event_id'
    """

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        owner = get_object_or_404(ClubOwner, email=email)
        club_profiles = ClubProfile.objects.filter(owner=owner)

        if not club_profiles.exists():
            return Response({"error": "No club profile found for this owner."}, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name')
        date = request.data.get('date')
        time = request.data.get('time')

        # Create event
        if name and date and time:
            club = club_profiles.first()
            serializer = EventSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(club=club)
                return Response({
                    "message": "Event created successfully!",
                    "created_event": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Otherwise, return all events for that owner
        events = Event.objects.filter(club__in=club_profiles).order_by('-date', '-time')
        serializer = EventSerializer(events, many=True)
        return Response({
            "owner_email": email,
            "total_events": events.count(),
            "events": serializer.data
        }, status=status.HTTP_200_OK)

    def get(self, request):
        """
        GET: Retrieve events by owner email (and optionally by event_id)
        """
        email = request.query_params.get('email')
        event_id = request.query_params.get('event_id')

        if not email:
            return Response({"error": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        owner = get_object_or_404(ClubOwner, email=email)
        club_profiles = ClubProfile.objects.filter(owner=owner)

        if not club_profiles.exists():
            return Response({"error": "No club profile found for this owner."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch single event if event_id provided
        if event_id:
            event = get_object_or_404(Event, id=event_id, club__in=club_profiles)
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Otherwise, list all events
        events = Event.objects.filter(club__in=club_profiles).order_by('-date', '-time')
        serializer = EventSerializer(events, many=True)
        return Response({
            "owner_email": email,
            "total_events": events.count(),
            "events": serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        PATCH: Update an existing event (by event_id + email)
        """
        email = request.data.get('email')
        event_id = request.data.get('event_id')

        if not email or not event_id:
            return Response({"error": "Both 'email' and 'event_id' are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        owner = get_object_or_404(ClubOwner, email=email)
        club_profiles = ClubProfile.objects.filter(owner=owner)

        event = get_object_or_404(Event, id=event_id, club__in=club_profiles)
        serializer = EventSerializer(event, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Event updated successfully.",
                "updated_event": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        DELETE: Delete an event (by event_id + email)
        """
        email = request.query_params.get('email') or request.data.get('email')
        event_id = request.query_params.get('event_id') or request.data.get('event_id')

        if not email or not event_id:
            return Response({"error": "Both 'email' and 'event_id' are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        owner = get_object_or_404(ClubOwner, email=email)
        club_profiles = ClubProfile.objects.filter(owner=owner)

        event = get_object_or_404(Event, id=event_id, club__in=club_profiles)
        event.delete()
        return Response({"message": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)





# dashboard views.py code 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models

class EventSummaryByOwnerEmailView(APIView):
    def get(self, request):
        email = request.GET.get('email')

        if not email:
            return Response({"error": "Email is required as GET param."},
                            status=status.HTTP_400_BAD_REQUEST)

        owner = get_object_or_404(ClubOwner, email=email)
        club_profiles = ClubProfile.objects.filter(owner=owner)

        if not club_profiles.exists():
            return Response({"error": "No club profile found for this owner."},
                            status=status.HTTP_404_NOT_FOUND)


        today = timezone.now()
        first_day = today.replace(day=1)

        # Filter events of this month
        events = Event.objects.filter(
            club__in=club_profiles,
            date__gte=first_day.date(),
            date__lte=today.date()
        )

        # Total monthly events
        total_events = events.count()

        # Live events (assume status="live")
        live_events = events.filter(status="live")

        # Live event names
        live_event_names = list(live_events.values_list("name", flat=True))

        # Total views
        total_views = events.aggregate(total=models.Sum("views"))["total"] or 0

        # Live event details (name + views)
        live_event_details = [
            {
                "name": e.name,
                "views": e.views
            }
            for e in live_events
        ]

        return Response({
            "owner_email": email,
            "current_month": today.strftime("%B %Y"),
            "current_month_total_events": total_events,
            "current_month_live_events": live_events.count(),
            "current_month_total_views": total_views,
            "live_event_names": live_event_names,
            "live_event_details": live_event_details
        })

# Event increase view count API view

class EventDetailView(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        
        event.views += 1
        event.save(update_fields=["views"])

        serializer = EventSerializer(event)
        return Response(serializer.data)




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


# class EventListCreateAPIView(APIView):
#     authentication_classes = [ClubOwnerAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
   
#         events = Event.objects.filter(club__owner=request.user)
#         serializer = EventSerializer(events, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
    
#         serializer = EventSerializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)





from .models import Event
from .models import ClubProfile  
from .serializers import EventSerializer  
from rest_framework.decorators import permission_classes

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_owner_events(request, owner_id):
    """
    Get all events under a specific club owner.
    """
    # Get all clubs owned by this owner
    clubs = ClubProfile.objects.filter(owner_id=owner_id)
    if not clubs.exists():
        return Response({"message": "No clubs found for this owner"}, status=status.HTTP_404_NOT_FOUND)

    # Get all events for those clubs
    events = Event.objects.filter(club__in=clubs).order_by('-date', '-time')
    if not events.exists():
        return Response({"message": "No events found for this owner"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventSerializer(events, many=True)
    return Response({"total_events": len(serializer.data), "events": serializer.data}, status=status.HTTP_200_OK)














@api_view(['GET'])
def get_all_events(request):
    events = Event.objects.all().order_by('-date', '-time')
    serializer = Get_all_EventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_upcoming_events(request):
    print("\n========== [DEBUG] get_upcoming_events Called ==========")

    # Step 1️⃣: Get today's date
    today = timezone.now().date()
    print(f"[DEBUG] Today's date: {today}")

    # Step 2️⃣: Filter all events happening today or later
    events = Event.objects.filter(date__gte=today).order_by('date', 'time')
    print(f"[DEBUG] Total events found (from today onwards): {events.count()}")

    # Step 3️⃣: Separate today's and future events
    today_events = events.filter(date=today)
    upcoming_events = events.filter(date__gt=today)

    print(f"[DEBUG] Today's events: {today_events.count()} | Future events: {upcoming_events.count()}")

    # Step 4️⃣: Merge today's events first, then future ones
    combined_events = list(today_events) + list(upcoming_events)

    # Step 5️⃣: Serialize and respond
    serializer = Get_all_EventSerializer(combined_events, many=True)
    print(f"[INFO] Returning {len(serializer.data)} total upcoming events (today first).")

    return Response(serializer.data, status=status.HTTP_200_OK)



#Club Profile views
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def club_detail_update(request, club_id):
    """
    GET -> Club details with average rating & reviews
    PATCH -> Update clubName and clubImageUrl
    """
    club = get_object_or_404(ClubProfile, id=club_id)

    
    if request.method == 'GET':
        reviews_data = club.reviews if isinstance(club.reviews, list) else []

        # calculate average rating
        if reviews_data:
            total_rating = sum(float(r.get('rating', 0)) for r in reviews_data)
            avg_rating = round(total_rating / len(reviews_data), 1)
        else:
            avg_rating = 0.0

        response_data = {
            "id": club.id,
            "clubName": club.clubName,
            "clubImageUrl": club.clubImageUrl.url if club.clubImageUrl else None,
            "insta_link": club.insta_link,
            "tiktok_link": club.tiktok_link,
            "phone": club.phone,
            "email": club.email,
            "average_rating": avg_rating,
            "total_reviews": len(reviews_data),
            "reviews": reviews_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


    elif request.method == 'PATCH':
        club_name = request.data.get('clubName')
        image = request.FILES.get('clubImageUrl')

        if club_name:
            club.clubName = club_name

        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            club.clubImageUrl = filename

        club.save()

        return Response({"message": "Club updated successfully"}, status=status.HTTP_200_OK)












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

from rest_framework.permissions import IsAuthenticated
# authentication_classes = [ClubOwnerAuthentication]
permission_classes = [IsAuthenticated]
class WeeklyHoursAPIView(APIView):
    """
    GET:
        - Provide 'email' in request body or query params.
        - Returns weekly hours for the owner's last ClubProfile.
    PATCH:
        - Provide 'email' and 'weekly_hours' data to update.
    """

    def get_object(self, email):
        try:
            owner = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            raise Http404("Owner not found with this email.")

        profiles = ClubProfile.objects.filter(owner=owner)
        if not profiles.exists():
            raise Http404("Club Profile not found for this owner.")

        return profiles.last()

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email') or request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        club_profile = self.get_object(email)
        serializer = WeeklyHoursSerializer(club_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        club_profile = self.get_object(email)
        weekly_hours_data = request.data.get('weekly_hours')

        if not weekly_hours_data:
            return Response({"error": "weekly_hours data is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WeeklyHoursSerializer(
            club_profile, data={"weekly_hours": weekly_hours_data}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        success_data = {
            "message": "Weekly hours updated successfully!",
            "weekly_hours": serializer.data.get('weekly_hours')
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




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import ClubProfile


class AllClubListView(APIView):
 
    permission_classes = [AllowAny]

    def get(self, request):
        clubs = ClubProfile.objects.all()

        if not clubs.exists():
            return Response(
                {"message": "No clubs found"},
                status=status.HTTP_200_OK
            )

        data = []
        for club in clubs:
            data.append({
                "id": club.id,
                "club_name": club.venue_name,
                "venue_city": club.venue_city,
                "about": club.about,
                "coverCharge": club.coverCharge,
                "ageRequirement": club.ageRequirement,
                "latitude": club.latitude,
                "longitude": club.longitude,
                "club_type": [ct.name for ct in club.club_type.all()],
                "vibes": [v.name for v in club.vibes_type.all()],
                "features": club.features,
                "image": club.clubImageUrl.url if club.clubImageUrl else None,
                "insta_link": club.insta_link,
                "tiktok_link": club.tiktok_link,
                "is_favourite": club.is_favourite,
                "click_count": club.click_count,
            })

        return Response(data, status=status.HTTP_200_OK)




# all club by get 


@api_view(['GET'])
def get_all_clubs(request):
    clubs = ClubProfile.objects.all()
    data = []

    for club in clubs:

        reviews_data = club.user_reviews if isinstance(club.user_reviews, list) else []

        if reviews_data:
            total_rating = sum(float(r['rating']) for r in reviews_data if 'rating' in r)
            avg_rating = round(total_rating / len(reviews_data), 1)
        else:
            avg_rating = 0.0

        data.append({
            "id": club.id,
            "owner": club.owner.full_name if club.owner else None,
            "clubName": club.venue_name,
            "club_city" : club.venue_city , 
            "about" : club.about,
            "weekly_hours" : club.weekly_hours,
            "club_type": [ct.name for ct in club.club_type.all()],
            "vibes_type": [v.name for v in club.vibes_type.all()],
            "clubImageUrl": club.clubImageUrl.url if club.clubImageUrl else None,
            "features": club.features,
            "events": club.events,
            "crowd_atmosphere": club.crowd_atmosphere,
            "is_favourite": club.is_favourite,
            "is_hidden" : club.is_hidden , 
            "club_review" : club.user_reviews,
            "insta_link" : club.insta_link,
            "tiktok_link" : club.tiktok_link,

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
            debug_logs.append(f"Club: {club.venue_name}, location: ({club.latitude}, {club.longitude}), distance={distance:.2f} km")
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


@api_view(['GET', 'POST', 'PATCH'])
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
            total_rating = sum(float(r.get('rating', 0)) for r in reviews_data)
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

    # ================= PATCH REQUEST =================
    elif request.method == 'PATCH':
        review_index = request.data.get('review_index')  # which review to edit
        rating = request.data.get('rating')
        comment = request.data.get('comment')
        image = request.FILES.get('image', None)

        if review_index is None:
            return Response({"error": "review_index is required to update a review"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            review_index = int(review_index)
        except ValueError:
            return Response({"error": "review_index must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Make sure club has reviews and that index exists
        if not isinstance(club.reviews, list) or review_index < 0 or review_index >= len(club.reviews):
            return Response({"error": "Invalid review index"}, status=status.HTTP_400_BAD_REQUEST)

        review = club.reviews[review_index]

        # Update fields if provided
        if rating:
            review['rating'] = float(rating)
        if comment:
            review['comment'] = comment
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            review['image_url'] = fs.url(filename)

        review['timestamp'] = datetime.now().isoformat()

        # Save updated review back to the list
        club.reviews[review_index] = review
        club.save()

        total_rating = sum(float(r.get('rating', 0)) for r in club.reviews)
        avg_rating = round(total_rating / len(club.reviews), 1)

        return Response({
            "success_msg": "Review updated successfully",
            "updated_review": review,
            "average_rating": avg_rating,
            "total_reviews": len(club.reviews)
        }, status=status.HTTP_200_OK)










# 2nd review views.py 


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def manage_club_reviewed(request, club_id):
    try:
        club = ClubProfile.objects.get(id=club_id)
    except ClubProfile.DoesNotExist:
        return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

    user_profile = UserProfile.objects.get(user=request.user)  

    # ================= GET REQUEST =================
    if request.method == 'GET':
        all_profiles = UserProfile.objects.all()
        reviews_data = []


        for profile in all_profiles:
            if isinstance(profile.user_reviews, list):
                reviews_data.extend(
                    [r for r in profile.user_reviews if r.get('club_id') == club.id]
                )

        if reviews_data:
            total_rating = sum(float(r.get('rating', 0)) for r in reviews_data)
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
        comment = request.data.get('comment')
        email = request.user.email
        image = request.FILES.get('image')

        if not rating:
            return Response({"error": "Rating is required"}, status=status.HTTP_400_BAD_REQUEST)

        image_url = None
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_url = fs.url(filename)

        new_review = {
            'club_id': club.id,  
            'rating': float(rating),
            'comment': comment,
            'image_url': image_url,
            'user_email': email,
            'timestamp': datetime.now().isoformat()
        }

        if not isinstance(user_profile.user_reviews, list):
            user_profile.user_reviews = []

        user_profile.user_reviews.append(new_review)
        user_profile.save()

        return Response({
            "success_msg": "Review submitted successfully",
            "new_review": new_review
        }, status=status.HTTP_201_CREATED)

    # ================= PATCH REQUEST =================
    elif request.method == 'PATCH':
        review_index = request.data.get('review_index')
        rating = request.data.get('rating')
        comment = request.data.get('comment')
        image = request.FILES.get('image')

        if review_index is None:
            return Response({"error": "review_index is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            review_index = int(review_index)
        except ValueError:
            return Response({"error": "review_index must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure user editing their own review only
        if review_index < 0 or review_index >= len(user_profile.user_reviews):
            return Response({"error": "Invalid review index"}, status=status.HTTP_400_BAD_REQUEST)

        review = user_profile.user_reviews[review_index]

        if review.get('club_id') != club.id:
            return Response({"error": "You can only edit your own review for this club"}, status=status.HTTP_403_FORBIDDEN)

        if rating:
            review['rating'] = float(rating)
        if comment:
            review['comment'] = comment
        if image:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            review['image_url'] = fs.url(filename)

        review['timestamp'] = datetime.now().isoformat()

        user_profile.user_reviews[review_index] = review
        user_profile.save()

        return Response({
            "success_msg": "Review updated successfully",
            "updated_review": review
        }, status=status.HTTP_200_OK)








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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from .serializers import UserFollowSerializer

User = get_user_model()


class FollowingPageView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            print(f"[DEBUG] User found: {user.email} (id={user.id})")
        except User.DoesNotExist:
            print(f"[ERROR] User not found: {email}")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Step  Get following and followers
        following_users = user.following.all()
        follower_users = user.followers.all()
        print(f"[DEBUG] Following count: {following_users.count()}, Follower count: {follower_users.count()}")

        # Step : Compute suggestion users
        follower_ids = follower_users.values_list("id", flat=True)
        following_ids = following_users.values_list("id", flat=True)

        # Users who follow you but you don't follow them (follow-back)
        follow_back_users = User.objects.filter(id__in=follower_ids).exclude(id__in=following_ids)
        exclude_ids = list(following_ids) + list(follow_back_users.values_list("id", flat=True)) + [user.id]
        other_suggestions = User.objects.exclude(id__in=exclude_ids)[:10]

        suggestions = list(follow_back_users) + list(other_suggestions)
        print(f"[DEBUG] Suggestions count: {len(suggestions)}")

        # Step 5: Serialize data
        context = {"request": request, "current_user": user}
        following_serializer = UserFollowSerializer(following_users, many=True, context=context)
        follower_serializer = UserFollowSerializer(follower_users, many=True, context=context)
        suggestion_serializer = UserFollowSerializer(suggestions, many=True, context=context)

        # Step  Response payload
        response_data = {
            "user_id": user.id,
            "follower_list": follower_serializer.data,
            "following_list": following_serializer.data,
            "suggestions": suggestion_serializer.data,
        }

        print(f"[INFO] Response ready — {len(follower_serializer.data)} followers, "
              f"{len(following_serializer.data)} following, {len(suggestion_serializer.data)} suggestions.")

        return Response(response_data, status=status.HTTP_200_OK)
    





from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['PATCH'])
def update_follow_status(request):
    """
    PATCH API:
    Body Example:
    {
        "user_email": "current_user@example.com",
        "target_email": "target_user@example.com",
        "follow_status": true
    }
    """
    print("\n========== [DEBUG] update_follow_status called ==========")

    user_email = request.data.get("user_email")
    target_email = request.data.get("target_email")
    follow_status = request.data.get("follow_status")

    if not user_email or not target_email:
        print("[ERROR] Missing user_email or target_email")
        return Response({"error": "user_email and target_email are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=user_email)
        target_user = User.objects.get(email=target_email)
    except User.DoesNotExist:
        print("[ERROR] One of the users not found")
        return Response({"error": "Invalid user email(s)"}, status=status.HTTP_404_NOT_FOUND)

    # Prevent self-following
    if user == target_user:
        return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

  
    if follow_status is True:
        user.following.add(target_user)
        message = f"{user.email} followed {target_user.email}"
        print(f"[INFO] {message}")
    elif follow_status is False:
        user.following.remove(target_user)
        message = f"{user.email} unfollowed {target_user.email}"
        print(f"[INFO] {message}")
    else:
        print("[ERROR] Invalid follow_status (must be true or false)")
        return Response({"error": "follow_status must be true or false"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": message,
        "user_id": user.id,
        "target_id": target_user.id,
        "follow_status": follow_status
    }, status=status.HTTP_200_OK)









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
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import UserLocation
from .serializers import UserLocationSerializer

class UpdateUserLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not latitude or not longitude:
            return Response({'error': 'latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        # save or update location
        location, created = UserLocation.objects.update_or_create(
            user=request.user,
            defaults={'latitude': latitude, 'longitude': longitude}
        )

        serializer = UserLocationSerializer(location)
        return Response({'message': 'Location updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)




#************************************************************************************************
# Final Recommedation api 
#************************************************************************************************

import logging
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import ClubProfile
from .utils import calculate_distance, get_coordinates_from_city

logger = logging.getLogger(__name__)
User = get_user_model()


class RecommendClubsView(APIView):

    def post(self, request):
        logger.info("=== [RecommendClubsView] API Called ===")
        logger.info(f"Incoming request: {request.data}")

        user_email = request.data.get("email")
        if not user_email:
            return Response({"error": "Email is required"}, status=400)

        # Fetch user
        try:
            user = User.objects.get(email=user_email)
            user_profile = user.userprofile
        except:
            logger.error("User not found")
            return Response({"error": "User not found"}, status=404)

        # -------------------------
        # USER LOCATION
        # -------------------------
        if user_profile.latitude and user_profile.longitude:
            user_lat = float(user_profile.latitude)
            user_lon = float(user_profile.longitude)
        else:
            logger.info(f"Fetching Geoapify coordinates for city: {user_profile.city}")
            user_lat, user_lon = get_coordinates_from_city(user_profile.city)

            if not user_lat:
                return Response({"error": "Cannot fetch user coordinates"}, status=400)

        # User vibes
        user_music = set(user_profile.music_preferences.values_list("name", flat=True))
        user_vibes = set(user_profile.ideal_vibes.values_list("name", flat=True))
        user_crowd = set(user_profile.crowd_atmosphere.values_list("name", flat=True))

        recommended = []
        clubs = ClubProfile.objects.all()

        # -------------------------
        # CLUB LOOP
        # -------------------------
        for club in clubs:

            # ----------------------------------------
            # GET CLUB LOCATION USING venue_city
            # ----------------------------------------
            if club.latitude and club.longitude:
                club_lat = float(club.latitude)
                club_lon = float(club.longitude)
            else:
                logger.info(f"Fetching Geoapify coordinates for club city: {club.venue_city}")

                club_lat, club_lon = get_coordinates_from_city(club.venue_city)

                if not club_lat:
                    logger.warning(f"Skipping {club.venue_name}: cannot fetch coordinates")
                    continue

                # Save to database once fetched (so no future API calls)
                club.latitude = club_lat
                club.longitude = club_lon
                club.save(update_fields=["latitude", "longitude"])
                logger.info(f"Saved coordinates for club {club.venue_name}")

            # -------------------------
            # Distance
            # -------------------------
            distance = calculate_distance(user_lat, user_lon, club_lat, club_lon)
            logger.info(f"{club.venue_name} distance: {distance:.2f} km")

            if distance > 30:
                continue

            # Club JSON fields
            club_music = set(club.features.keys()) if club.features else set()
            club_vibes = set(club.events.keys()) if club.events else set()
            club_crowd = set(club.crowd_atmosphere.keys()) if club.crowd_atmosphere else set()

            # -------------------------
            # Scoring
            # -------------------------
            score = 0

            if user_music.intersection(club_music):
                score += 25

            if user_vibes.intersection(club_vibes):
                score += 35

            if user_crowd.intersection(club_crowd):
                score += 25

            if distance <= 10:
                score += 15

            recommended.append({
                "club_id": club.id,
                "name": club.venue_name,
                "city": club.venue_city,
                "distance_km": round(distance, 2),
                "score": score,
            })

        # Sort
        recommended = sorted(recommended, key=lambda x: x["score"], reverse=True)

        if not recommended:
            return Response({"message": "No nearby club found"}, status=200)

        return Response({"recommended_clubs": recommended[:5]}, status=200)



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

    clubs = ClubProfile.objects.all()
    recommendations = []

    for club in clubs:

        if club.latitude is None or club.longitude is None:
            continue

        distance = calculate_distance(user_lat, user_lon,
                                     float(club.latitude),
                                     float(club.longitude))

        if distance > 15: 
            continue

        
        club_music = set(club.features.get('music', []))
        club_vibes = set(club.events.get('vibes', []))
        club_crowd = set(club.crowd_atmosphere.get('crowd', []))

        
        music_match = len(user_music & club_music)
        vibes_match = len(user_vibes & club_vibes)
        crowd_match = len(user_crowd & club_crowd)

        total_match = music_match + vibes_match + crowd_match

        if total_match > 0:
            recommendations.append({
                "id": club.id,
                "name": club.venue_name,
                "total_match": total_match,
                "distance_km": round(distance, 2)
            })

    if not recommendations:
        return Response({"message": "No recommended club found"}, status=404)

    top_club = sorted(recommendations,
                      key=lambda x: (-x['total_match'], x['distance_km']))[0]

    return Response(top_club, status=200)




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
    return Response({"message": f"{club.email} clicked", "total_clicks": club.click_count}, status=status.HTTP_200_OK)

from .models import ClubProfile
from .serializers import ClubProfileSerializered


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trendy_club(request):
    


    clubs = ClubProfile.objects.all().order_by('-click_count')

    if not clubs.exists():
        print("[INFO] No clubs found in database.")
        return Response({"message": "No clubs available."}, status=status.HTTP_404_NOT_FOUND)

    print(f"[DEBUG] Found {clubs.count()} clubs sorted by click count.")


    serializer = ClubProfileSerializered(clubs, many=True, context={'request': request})

    response_data = {
        "count": len(serializer.data),
        "results": serializer.data,
    }

    print(f"[INFO] Returning {len(serializer.data)} trendy clubs.")
    return Response(response_data, status=status.HTTP_200_OK)





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
            debug_logs.append(f"Club: {club.email}, location: ({club.latitude}, {club.longitude}), distance={distance:.2f} km")
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
        debug_logs.append(f"Club: {club.venue_name}, distance={distance:.2f} km")

        if distance > 5:
            continue 

        weekly_hours = club.weekly_hours or {}
        today_hours = weekly_hours.get(today)
        if not today_hours:
            debug_logs.append(f"Club {club.venue_name} has no hours for today")
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

        return Response({"message": f"Club '{club.venue_name}' favourite status updated to {club.is_favourite}"}, status=status.HTTP_200_OK)

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
    


# Is Hidden
@api_view(['GET', 'PATCH'])
def hidden_clubs(request):
   
    if request.method == 'PATCH':
        club_id = request.data.get('club_id')
        is_fav = request.data.get('is_hidden')

        if club_id is None or is_fav is None:
            return Response({"error": "club_id and is_hidden are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            club = ClubProfile.objects.get(id=club_id)
        except ClubProfile.DoesNotExist:
            return Response({"error": "Club not found"}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(is_fav, str):
            is_fav = is_fav.lower() in ['true', '1', 'yes']

        club.is_favourite = bool(is_fav)
        club.save()

        return Response({"message": f"Club '{club.venue_name}' hidden status updated to {club.is_favourite}"}, status=status.HTTP_200_OK)

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
                "is_favourite": club.is_hidden,
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


    full_name = request.data.get('full_name')
    if full_name is not None:
        user.full_name = full_name
        user.save(update_fields=['full_name'])


    city = request.data.get('city')
    if city is not None:
        profile.city = city


    about = request.data.get('about')
    if about is not None:
        profile.about = about


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





# For plan to night views.py 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Q
import random

from .models import ClubProfile, Vibes_Choice


class ClubSelectionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        GET:
        Return vibe and who-with options (and optional club list preview)
        """

        vibe_options = list(Vibes_Choice.objects.values_list('name', flat=True)) or [
            "Chill", "Party", "Romantic", "Luxury", "Live Music"
        ]

        who_with_options = ["Friends", "Partner", "Family", "Alone"]

        # Optional: preview 3 random clubs
        clubs = ClubProfile.objects.all()
        random_clubs = random.sample(list(clubs[:10]), min(3, clubs.count())) if clubs.exists() else []

        data = {
            "clubs_preview": [
                {"id": club.id, "name": club.venue_name, "city": club.venue_city}
                for club in random_clubs
            ],
            "vibes": vibe_options,
            "who_are_you_with": who_with_options,
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        POST:
        Find matching clubs by selected vibe.
        Example body:
        {
            "email": "user@example.com",
            "selected_vibe": "Party",
            "who_are_you_with": "Friends"
        }
        """
        email = request.data.get("email")
        selected_vibe = request.data.get("selected_vibe")
        who_with = request.data.get("who_are_you_with")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not selected_vibe:
            return Response({"error": "Vibe selection is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not who_with:
            return Response({"error": "Please select who you are with"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vibe_obj = Vibes_Choice.objects.get(name__iexact=selected_vibe)
        except Vibes_Choice.DoesNotExist:
            return Response({"error": f"Vibe '{selected_vibe}' not found"}, status=status.HTTP_404_NOT_FOUND)

        matching_clubs = ClubProfile.objects.filter(vibes_type=vibe_obj)

        if not matching_clubs.exists():
            return Response({
                "message": f"No clubs found for vibe '{selected_vibe}'",
                "vibe": selected_vibe,
                "with": who_with
            }, status=status.HTTP_200_OK)

  
        clubs = random.sample(list(matching_clubs), min(3, matching_clubs.count()))

        data = {
            "message": "Matching clubs found!",
            "selected_vibe": selected_vibe,
            "who_are_you_with": who_with,
            "clubs": [
                {
                    "id": club.id,
                    "name": club.venue_name,
                    "city": club.venue_city,
                    "club_type": [ct.name for ct in club.club_type.all()],
                    "vibes": [v.name for v in club.vibes_type.all()],
                    "coverCharge": club.coverCharge,
                    "image": club.clubImageUrl.url if club.clubImageUrl else None,
                }
                for club in clubs
            ],
        }

        return Response(data, status=status.HTTP_200_OK)





# for owner details api 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import ClubOwner, ClubProfile


class OwnerClubDetailsView(APIView):
    """
    POST:
    Get Club details by Owner Email.

    Example Request:
    {
        "email": "owner@example.com"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            owner = ClubOwner.objects.get(email=email)
        except ClubOwner.DoesNotExist:
            return Response({"error": "Owner not found"}, status=status.HTTP_404_NOT_FOUND)

    
        try:
            club = owner.club_profile  
        except ClubProfile.DoesNotExist:
            return Response({"error": "Club profile not found for this owner"}, status=status.HTTP_404_NOT_FOUND)


        data = {
            "owner_email": owner.email,
            "owner_full_name":owner.full_name,
            "owner_profile_image": owner.profile_image.url if owner.profile_image else None,
            "club_name": club.venue_name,
            "venue_city": club.venue_city,
            "about": club.about,
            "coverCharge": club.coverCharge,
            "ageRequirement": club.ageRequirement,
            "latitude": club.latitude,
            "longitude": club.longitude,
            "club_type": [ct.name for ct in club.club_type.all()],
            "vibes": [v.name for v in club.vibes_type.all()],
            "features": club.features,
            "events": club.events,
            "crowd_atmosphere": club.crowd_atmosphere,
            "image": club.clubImageUrl.url if club.clubImageUrl else None,
            "insta_link": club.insta_link,
            "tiktok_link": club.tiktok_link,
            "phone": club.phone,
            "click_count": club.click_count,
            "is_favourite": club.is_favourite,
        }

        return Response(data, status=status.HTTP_200_OK)












from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserProfileSerializer

@api_view(['GET'])
@permission_classes([AllowAny])  # Public API
def get_all_user_profiles(request):
    print("\n========== [DEBUG] Get All User Profiles Called ==========")
    try:
        profiles = UserProfile.objects.select_related('user').prefetch_related(
            'music_preferences', 'ideal_vibes', 'crowd_atmosphere'
        )
        print(f"[DEBUG] Total profiles fetched: {profiles.count()}")

        serializer = UserProfileSerializer(profiles, many=True, context={'request': request})
        print(f"[DEBUG] Serialization successful. Returning {len(serializer.data)} profiles.")

        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })
    except Exception as e:
        print(f"[ERROR] Failed to fetch user profiles: {e}")
        return Response({"error": "Something went wrong while fetching profiles"}, status=500)






# Twilio integration views.py  + send otp 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import User
from .utils import generate_otp, send_otp_sms_infobip

class ForgotPasswordMobileAPIView(APIView):
    """
    POST /auth/forgot-password-mobile/
    Body: { "email": "user@gmail.com", "phone_number": "+8801743418894" }
    """

    def post(self, request):
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")

        if not email or not phone_number:
            return Response(
                {"error": "Email and phone_number are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "If your email exists, OTP has been sent."},
                status=status.HTTP_200_OK
            )

     
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()


        success = send_otp_sms_infobip(phone_number, otp)
        if success:
       
            request.session["pending_phone_number"] = phone_number
            request.session["pending_user_email"] = email
            return Response(
                {"message": f"OTP sent successfully to {phone_number}"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Failed to send OTP via Infobip."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





# verify otp 
class VerifyMobileOTPAPIView(APIView):
    """
    POST /auth/verify-mobile-otp/
    Body: { "email": "user@gmail.com", "otp": "1234", "phone_number": "+8801743418894" }
    """

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        phone_number = request.data.get("phone_number")

        if not email or not otp or not phone_number:
            return Response({"error": "Email, phone_number & OTP required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        from datetime import timedelta
        if not user.otp or timezone.now() > user.otp_created_at + timedelta(minutes=5):
            return Response({"error": "OTP expired. Try again."},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.otp != otp:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


        user.phone_number = phone_number
        user.otp = None
        user.is_active = True
        user.save()

        return Response(
            {"message": "Phone verified successfully & saved."},
            status=status.HTTP_200_OK
        )









# Use Google Places API to get popular nightclubs in NYC

import requests
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .services import (
    GOOGLE_API_KEY,
    fetch_nyc_nightclubs_textsearch,
    fetch_place_details,
    build_photo_url
)


class NYCNightclubsAPIView(APIView):
    """
    GET /api/places/nyc-nightclubs/?limit=20

    Returns up to `limit` (default 20) popular nightclubs in New York City.
    Uses Google Places Text Search + Place Details.
    Results are cached for 10 minutes.
    """

    CACHE_KEY = 'nyc_nightclubs_v1'
    CACHE_TTL = 60 * 10  # 10 minutes

    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        limit = max(1, min(limit, 50))  # limit between 1–50

        # Check cache
        cached = cache.get(self.CACHE_KEY)
        if cached:
            data = cached[:limit]
            return Response({"count": len(data), "results": data})

        if not GOOGLE_API_KEY:
            return Response(
                {"detail": "Google API key not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            # 1) Text search for NYC nightclubs
            text_res = fetch_nyc_nightclubs_textsearch(GOOGLE_API_KEY)

            if text_res.get("status") not in ("OK", "ZERO_RESULTS"):
                return Response(
                    {"detail": "Google Places Text Search error", "status": text_res.get("status")},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            candidates = text_res.get("results", [])

            # Sort by popularity
            def popularity_key(p):
                return (
                    p.get("rating") or 0,
                    p.get("user_ratings_total") or 0
                )

            candidates_sorted = sorted(candidates, key=popularity_key, reverse=True)
            selected = candidates_sorted[:limit]

            results = []

            for item in selected:
                place_id = item.get("place_id")

                # 2) Details API call
                details_json = fetch_place_details(GOOGLE_API_KEY, place_id)

                if details_json.get("status") != "OK":
                    continue

                d = details_json.get("result", {})

                photos = []
                for p in d.get("photos", [])[:5]:
                    ref = p.get("photo_reference")
                    if ref:
                        photos.append(build_photo_url(GOOGLE_API_KEY, ref))

                geom = d.get("geometry", {}).get("location", {})

                results.append({
                    "place_id": d.get("place_id"),
                    "name": d.get("name"),
                    "address": d.get("formatted_address"),
                    "lat": geom.get("lat"),
                    "lng": geom.get("lng"),
                    "rating": d.get("rating"),
                    "user_ratings_total": d.get("user_ratings_total"),
                    "phone": d.get("formatted_phone_number") or d.get("international_phone_number"),
                    "website": d.get("website"),
                    "opening_hours": d.get("opening_hours"),
                    "photos": photos,
                    "maps_url": d.get("url"),
                })

            # Cache for 10 minutes
            cache.set(self.CACHE_KEY, results, timeout=self.CACHE_TTL)

            return Response({"count": len(results), "results": results})

        except requests.HTTPError as e:
            return Response(
                {"detail": "Error calling Google APIs", "error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        except Exception as e:
            return Response(
                {"detail": "Internal error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
