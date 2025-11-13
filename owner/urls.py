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
#              CLUB OWNER ENDPOINTS               
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

# -----------------------   CLUB OWNER DETAILS API  -----------------
    path('owner/club-profile/', ClubProfileByEmailView.as_view(), name='club-profile-by-email'),
    path('events/by-owner-email/', EventsByOwnerEmailView.as_view(), name='events-by-owner-email'),

    path('owner/legal-content/<slug:type_slug>/', LegalContentView.as_view(), name='legal-content'),
    path('owner/club-profile/weekly-hours/', WeeklyHoursAPIView.as_view(), name='club-profile-weekly-hours'),
    # path('owner/events/', EventListCreateAPIView.as_view(), name='event-list-create'),


  
    path('club-recomend-info/<int:pk>/', ClubDetailView.as_view(), name='club-detail'),
    path('owner/dashborad-status/', DashboardStatsView.as_view(), name='club-detail'),
    path('owner/anlytical-dashborad-status/', AnalyticalDashboard.as_view(), name='club-'),

    path('owner/club-types/', ClubTypeListAPIView.as_view(), name='club-type-list'),
    path('owner/vibes-choices/', VibesChoiceListAPIView.as_view(), name='vibes-choice-list'),
    path('owner/<int:owner_id>/events/', get_owner_events, name='get_owner_events'), # search by clubowner id 
    path('club/<int:club_id>/', club_detail_update, name='club_detail_update'), # edit club profile
 
 
    


    # path('owner/clubs/<int:club_id>/reviews/', ClubReviewListCreateView.as_view(), name='club-reviews'),











#=============================================================================================
#=============================================================================================
#                  USER SIDE ENDPOINTS               
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
    path('user/forgot-password-mobile/', ForgotPasswordMobileAPIView.as_view(), name='forgot-password-mobile'),
    path('user/verify-mobile-otp/', VerifyMobileOTPAPIView.as_view(), name='verify-mobile-otp'), #Twilio OTP--------------------
    path('user/reset-password/', UserResetPasswordAPIView.as_view(), name='user-reset-password'),
    path('user/update-location/', UpdateUserLocationView.as_view(), name='update-location'),   ### user location  api

    path('user/places/', views.get_place_details, name='place-details'),
    path('clubs/<int:club_id>/reviews/', manage_club_reviews, name='manage-club-reviews'),
    path('clubs/<int:club_id>/user_review/', manage_club_reviewed, name='manage-club-redsfviews'), #review #review
    path('manage_user_profile_preferences/', manage_user_profile_preferences, name='manage-ideal-vibes'),
    path('following/', FollowingPageView.as_view(), name='following-page'),
    path('follow/update/', update_follow_status, name='update_follow_status'),#  Follow patch requ

    path('users/<int:user_id>/toggle-follow/', FollowToggleView.as_view(), name='toggle-follow'),
    path('profile/', UserProfileView.as_view(), name='user-profile'), 
    path('clubs/recommend/', RecommendClubsView.as_view(), name='recommend-clubs'), # User preference details api
    path('trendy-club/' , get_trendy_club , name= 'trendy') ,
    path('clubs/<int:club_id>/click/', views.club_click, name='club_click'),  # relation with trending
    path('all-events/', get_all_events, name='get_all_events'),
    path('events/upcoming/', get_upcoming_events, name='upcoming-events'),
    path('all-clubs/', get_all_clubs, name='get-all-clubs'),
    path('clubs-filter/', get_clubs_by_type_post, name='get-clubs-by-type'),
    path('clubs-nearby/', nearby_clubs, name='nearby-clubs'),
    path('clubs/open-today/', nearby_currently_open_clubs, name='clubs-open-today'),
    path('is_favourite/', favourite_clubs, name='clubs-en-today'),
    path('is_hidden/', hidden_clubs, name='hidden-en-today'),
    path('edit-user-profile/' , update_user_profile , name='edit-user-profile'),
    path('top-club-recommendation/' , top_recommended_club , name='top-club'),
    path("plan-tonight/selection/", ClubSelectionView.as_view(), name="club_selection"),  # plan night today
    path('owner/club-details/', OwnerClubDetailsView.as_view(), name='owner_club_details'),
    path('all-clubs/', AllClubListView.as_view(), name='all_clubs'),
    path('users-all/', get_all_user_profiles, name='get_all_user_profiles'),  #all user details


 














]