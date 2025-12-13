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

# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ClubOwner




@admin.register(ClubOwner)
class ClubOwnerAdmin(UserAdmin):
    model = ClubOwner

    ordering = ("email",)
    list_display = (  'id' , "email", "verification_status", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {
            "fields": (
                "full_name",
                "phone_number",
                "venue_name",
                "venue_address",
                "latitude",
                "longitude",
                "proof_doc",    

            )
        }),
        ("Status", {
            "fields": (
                "verification_status",
                "is_active",
                "assigned_club",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

    search_fields = ("email",)


  



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