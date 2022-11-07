from django.db.models.signals import post_save
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Profile


@receiver(user_signed_up)
def create_profile(sender, **kwargs):
    Profile.objects.create(user=kwargs['user'])


@receiver(user_signed_up)
def save_profile(sender, **kwargs):
    kwargs['user'].profile.save()
