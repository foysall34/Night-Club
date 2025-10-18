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

    path('clubowners/status/', get_all_clubowners_status, name='clubowners-status'),
    path('owner/register/', OwnerRegisterView.as_view(), name='register'),
    path('owner/verify-otp/', OwnerVerifyOTPView.as_view(), name='verify-otp'),
    path('owner/resend-otp/', OwnerResendOTPView.as_view(), name='resend-otp'),
    path('owner/log-in/', OwnerLoginView.as_view(), name='log-in'),
    path('owner/forgot-password/', OwnerForgotPasswordView.as_view(), name='forgot-password'),
    path('owner/reset-password/', OwnerPasswordResetView.as_view(), name='owner-reset-password'),
    # path('owner/change-password/', OwnerChangePasswordView.as_view(), name='change-password'),
    path('owner/clubs/', ClubProfileListCreateAPIView.as_view(), name='club-list-create'),
    path('owner/club-profiles/<int:pk>/', ClubProfileListCreateAPIView.as_view(), name='club-profile-detail'),
    path('owner/legal-content/<slug:type_slug>/', LegalContentView.as_view(), name='legal-content'),
    path('owner/club-profile/weekly-hours/', WeeklyHoursAPIView.as_view(), name='club-profile-weekly-hours'),
    path('owner/events/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('owner/events/<int:pk>/', EventRetrieveUpdateDestroyAPIView.as_view(), name='event-detail'),
    path('club-recomend-info/<int:pk>/', ClubDetailView.as_view(), name='club-detail'),
    path('owner/dashborad-status/', DashboardStatsView.as_view(), name='club-detail'),
    path('owner/anlytical-dashborad-status/', AnalyticalDashboard.as_view(), name='club-'),

    path('owner/club-types/', ClubTypeListAPIView.as_view(), name='club-type-list'),
    path('owner/vibes-choices/', VibesChoiceListAPIView.as_view(), name='vibes-choice-list'),
    


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
    path('user/reset-password/', UserResetPasswordAPIView.as_view(), name='user-reset-password'),
    path('owners/<int:owner_id>/clubs/', views.get_owners_clubs, name='owner-clubs-list'),   #See all club fillter by owner id 
    path('user/places/', views.get_place_details, name='place-details'),
    path('clubs/<int:club_id>/reviews/', manage_club_reviews, name='manage-club-reviews'),
    path('manage_user_profile_preferences/', manage_user_profile_preferences, name='manage-ideal-vibes'),
    path('following/', FollowingPageView.as_view(), name='following-page'),
    path('users/<int:user_id>/toggle-follow/', FollowToggleView.as_view(), name='toggle-follow'),
    path('profile/', UserProfileView.as_view(), name='user-profile'), 
    path('clubs/recommend/', recommend_clubs, name='recommend-clubs'), # User preference details api
    path('trendy-club/<int:owner_id>/' , get_trendy_club , name= 'trendy') ,
    path('clubs/<int:club_id>/click/', views.club_click, name='club_click'),
    path('all-events/', get_all_events, name='get_all_events'),
    path('events/upcoming/', get_upcoming_events, name='upcoming-events'),
    path('all-clubs/', get_all_clubs, name='get-all-clubs'),
    path('clubs-filter/', get_clubs_by_type_post, name='get-clubs-by-type'),
    path('clubs-nearby/', nearby_clubs, name='nearby-clubs'),
    path('clubs/open-today/', nearby_currently_open_clubs, name='clubs-open-today'),
    path('is_favourite/', favourite_clubs, name='clubs-en-today'),













]