from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import ClubOwner, ClubProfile, LegalContent, ClubType, Vibes_Choice,UserProfile, Event , MusicGenre , Vibe ,CrowdAtmosphere 



admin.site.register(Vibe)
admin.site.register(ClubType)
admin.site.register(CrowdAtmosphere)

admin.site.register(Vibes_Choice)
admin.site.register(LegalContent)
# admin.site.register(ClubProfile)
admin.site.register(UserProfile)


@admin.register(MusicGenre)
class MusicGenreAdmin(admin.ModelAdmin):

    list_display = ('name',)



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'club' , 'name' , 'status')


@admin.register(ClubProfile)
class ClubProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner' , 'venue_name')


import smtplib
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

@admin.register(ClubOwner)
class ClubOwnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'venue_name', 'venue_city', 'verification_status', 'is_active')
    list_filter = ('verification_status', 'is_active', 'date_joined')
    search_fields = ('email', 'full_name', 'venue_name')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')

    fieldsets = (
        ('Personal Information', {'fields': ('email', 'full_name', 'password', 'phone_number')}),
        ('Venue Information', {'fields': ('venue_name', 'venue_city', 'latitude', 'longitude')}),
        ('Status and Permissions', {'fields': ('verification_status', 'is_active', 'is_staff')}),
        ('Verification Documents', {'fields': ('proof_doc', 'id_front_page', 'id_back_page')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if change and 'verification_status' in form.changed_data:
            try:
                if obj.verification_status == 'approved':
                    subject = 'Your Club Registration Has Been Approved'
                    message = (
                        f'Dear {obj.full_name},\n\n'
                        f'We are pleased to inform you that your registration for the club "{obj.venue_name}" has been successfully approved. '
                        'You can now enjoy all the features of our platform.\n\n'
                        'Best regards,\nThe Team'
                    )
                elif obj.verification_status == 'rejected':
                    subject = 'Update on Your Club Registration'
                    message = (
                        f'Dear {obj.full_name},\n\n'
                        f'We are writing to inform you that after reviewing your application for "{obj.venue_name}", '
                        'we are unable to approve your registration at this time.\n\n'
                        'If you have any questions, please contact our support team.\n\n'
                        'Best regards,\nThe Team'
                    )
                else:
                    return

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.email],
                    fail_silently=False,
                )
                self.message_user(request, "Email notification sent successfully.", messages.SUCCESS)

            except smtplib.SMTPRecipientsRefused as e:
                self.message_user(
                    request,
                    f"Email not sent — recipient’s mailbox is temporarily unavailable: {e}",
                    messages.WARNING
                )

            except Exception as e:
                self.message_user(
                    request,
                    f"Unexpected error sending email: {e}",
                    messages.ERROR
                )






# For user admin.py *********
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
  
    list_display = ( 'id', 'email', 'full_name', 'is_active', 'is_staff', 'date_joined')
    
 
    search_fields = ('email', 'full_name', 'phone_number')

    ordering = ('-date_joined',)
    
 
    list_filter = ('is_active', 'is_staff', 'date_joined')

    fieldsets = (
      
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('OTP Information', {
            'fields': ('otp', 'otp_created_at'),
            'classes': ('collapse',), 
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password', 'password2'),
        }),
    )


    readonly_fields = ('last_login', 'date_joined', 'otp_created_at')

    filter_horizontal = ('groups', 'user_permissions',)