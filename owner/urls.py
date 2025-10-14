# accounts/urls.py
from django.urls import path
from .views import *
from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationAPIView,
    UserVerifyOTPAPIView,
    UserResendOTPAPIView,
    UserLoginAPIView,
    UserChangePasswordAPIView,
    UserForgotPasswordAPIView,
    UserResetPasswordAPIView,
)


urlpatterns = [
#=============================================================================================
#=============================================================================================
#              Club Owner   ENDPOINTS               
#=============================================================================================
#=============================================================================================


    path('owner/register/', OwnerRegisterView.as_view(), name='register'),
    path('owner/verify-otp/', OwnerVerifyOTPView.as_view(), name='verify-otp'),
    path('owner/resend-otp/', OwnerResendOTPView.as_view(), name='resend-otp'),
    path('owner/log-in/', OwnerLoginView.as_view(), name='log-in'),
    path('owner/forgot-password/', OwnerForgotPasswordView.as_view(), name='forgot-password'),
    # path('owner/change-password/', OwnerChangePasswordView.as_view(), name='change-password'),
    path('owner/clubs/', ClubProfileListCreateAPIView.as_view(), name='club-list-create'),
    path('owner/club-profiles/<int:pk>/', ClubProfileListCreateAPIView.as_view(), name='club-profile-detail'),
    path('owner/legal/<slug:type_slug>/', LegalContentView.as_view(), name='legal-content'),
    path('owner/club-profile/weekly-hours/', WeeklyHoursAPIView.as_view(), name='club-profile-weekly-hours'),
    path('owner/events/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('owner/events/<int:pk>/', EventRetrieveUpdateDestroyAPIView.as_view(), name='event-detail'),
    # path('owner/clubs/<int:club_id>/reviews/', ClubReviewListCreateView.as_view(), name='club-reviews'),











#=============================================================================================
#=============================================================================================
#=============================================================================================
#                  Normal user ALL API    ENDPOINTS               
#=============================================================================================
#=============================================================================================





    # User Account Management
    path('user/register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('user/verify-otp/', UserVerifyOTPAPIView.as_view(), name='user-verify-otp'),
    path('user/resend-otp/', UserResendOTPAPIView.as_view(), name='user-resend-otp'),

    # Authentication
    path('user/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Password Management
    path('user/change-password/', UserChangePasswordAPIView.as_view(), name='user-change-password'),
    path('user/forgot-password/', UserForgotPasswordAPIView.as_view(), name='user-forgot-password'),
    path('user/reset-password/<uidb64>/<token>/', UserResetPasswordAPIView.as_view(), name='user-reset-password'),
    path('owners/<int:owner_id>/clubs/', views.get_owners_clubs, name='owner-clubs-list'),
    path('user/places/', views.get_place_details, name='place-details'),
    path('clubs/<int:club_id>/reviews/', manage_club_reviews, name='manage-club-reviews'),
    path('profile/music-preferences/', manage_music_preferences, name='manage-music-preferences'),
    path('profile/ideal-vibes/', manage_ideal_vibes, name='manage-ideal-vibes'),
    path('profile/crowd-atmosphere/', manage_crowd_atmosphere, name='manage-crowd-atmosphere'),
    path('profile/nights-out/', manage_nights_out, name='manage-nights-out'),
    path('following/', FollowingPageView.as_view(), name='following-page'),
    path('users/<int:user_id>/toggle-follow/', FollowToggleView.as_view(), name='toggle-follow'),






]