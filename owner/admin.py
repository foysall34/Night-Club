# accounts/admin.py

from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import ClubOwner, ClubProfile, LegalContent, ClubType, Vibes_Choice, Event , UserProfile




# admin.site.register(Review)
admin.site.register(UserProfile)
admin.site.register(ClubType)
admin.site.register(Event)
admin.site.register(Vibes_Choice)
admin.site.register(LegalContent)



@admin.register(ClubProfile)
class ClubProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'clubName' )






@admin.register(ClubOwner)
class ClubOwnerAdmin(admin.ModelAdmin):
    """
    A class to customize the ClubOwner model in the admin panel.
    """
    
    list_display = (
        'id',
        'email', 
        'full_name', 
        'venue_name', 
        'verification_status', 
        'is_active', 
        'date_joined'
    )
    list_filter = ('verification_status', 'is_active')
    search_fields = ('email', 'full_name', 'venue_name')
    
    fieldsets = (
        ('Personal Information', {

            'fields': ('email', 'full_name', 'phone_number')
        }),
        ('Venue Information', {
            'fields': ('venue_name', 'venue_address', 'link')
        }),
        ('Proof of Ownership (Documents)', {
            'fields': ('profile_image', 'id_front_page', 'id_back_page')
        }),
        ('Status & Permissions', {
            'fields': ('is_active', 'verification_status', 'is_staff', 'is_superuser')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
      
    )
    readonly_fields = ('last_login', 'date_joined')

    def save_model(self, request, obj, form, change):
        """
        This method is called when a ClubOwner object is saved from the admin panel.
        Your custom email sending logic is preserved here.
        """
        if change and 'verification_status' in form.changed_data:
    
            
            if obj.verification_status == 'approved':

                subject = 'Your Club Registration Has Been Approved'
                message = (
                    f'Dear {obj.full_name},\n\n'
                    f'We are pleased to inform you that your registration for the club "{obj.venue_name}" has been successfully approved. '
                    'You can now enjoy all the features of our platform.\n\n'
                    'Best regards,\n'
                    'The Team'
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.email],
                    fail_silently=False,
                )
            
            elif obj.verification_status == 'rejected':
   
                subject = 'Your Club Registration Has Been Rejected'
                message = (
                    f'Dear {obj.full_name},\n\n'
                    f'We regret to inform you that your registration for the club "{obj.venue_name}" has been rejected. '
                    'This decision was made as your application did not meet our policy guidelines.\n\n'
                    'If you have any questions, please contact our support team.\n\n'
                    'Best regards,\n'
                    'The Team'
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.email],
                    fail_silently=False,
                )
        

        super().save_model(request, obj, form, change)









# For Norma user admin.py 


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ClubOwner
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for the regular User model.
    """
    # Fields to display in the list view
    list_display = ('email', 'full_name', 'is_active', 'is_staff', 'date_joined')
    
    # Fields to filter by in the right sidebar
    list_filter = ('is_active', 'is_staff', 'date_joined')
    
    # Fields to search by
    search_fields = ('email', 'full_name')
    
    # Default ordering
    ordering = ('-date_joined',)
    
    # Use fieldsets to organize the detail view form
    # Note: We are replacing the default 'username' with 'email'
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('OTP', {'fields': ('otp', 'otp_created_at')}),
    )

    # Fields to display when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone_number', 'password', 'password2'),
        }),
    )

    # Make certain fields read-only
    readonly_fields = ('last_login', 'date_joined', 'otp_created_at')