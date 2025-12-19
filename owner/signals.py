from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ClubOwner
from .utils import generate_otp, send_approval_email, send_rejection_email

@receiver(post_save, sender=ClubOwner)
def send_otp_on_approval(sender, instance, created, **kwargs):

    if created:
        return

    if instance.verification_status == "approved" and instance.otp is None:
        otp = generate_otp()
        instance.otp = otp
        instance.otp_created_at = timezone.now()
        instance.is_active = True
        instance.save()

        send_approval_email(instance.email, otp)

   
    if instance.verification_status == "rejected":
        send_rejection_email(instance.email)




# owner/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClubOwner, ClubProfile


@receiver(post_save, sender=ClubOwner)
def create_club_profile(sender, instance, created, **kwargs):
    if created:
        ClubProfile.objects.create(
            owner=instance,
            venue_name=instance.venue_name,
            venue_address=instance.venue_address,
            latitude=instance.latitude,
            longitude=instance.longitude,
            email=instance.email,
        )
