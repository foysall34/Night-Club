# accounts/admin.py

from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import ClubOwner, ClubProfile, LegalContent, ClubType, Vibes_Choice

# These registrations are correct and have been kept.
admin.site.register(ClubType)
admin.site.register(Vibes_Choice)
admin.site.register(LegalContent)
admin.site.register(ClubProfile)

@admin.register(ClubOwner)
class ClubOwnerAdmin(admin.ModelAdmin):
    """
    A class to customize the ClubOwner model in the admin panel.
    """
    
    list_display = (
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
            # --- FIX: Removed 'username' from this line as it does not exist on the ClubOwner model. ---
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
        # You may want to add the groups and user_permissions fields here if you need to manage them
        # ('Groups & Permissions', {
        #     'fields': ('groups', 'user_permissions')
        # })
    )
    readonly_fields = ('last_login', 'date_joined')

    def save_model(self, request, obj, form, change):
        """
        This method is called when a ClubOwner object is saved from the admin panel.
        Your custom email sending logic is preserved here.
        """
        if change and 'verification_status' in form.changed_data:
            # Send an email only if the verification status has changed
            
            if obj.verification_status == 'approved':
                # Send approval email
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
                # Send rejection email
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
        
        # It is crucial to call the super() method to save the object
        super().save_model(request, obj, form, change)