from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from social_media.models import Profile


@receiver(post_save, sender=get_user_model())
def create_profile_signal(sender, instance, created, **kwargs):
    if created:
        username = instance.email.split("@")[0]
        profile = Profile(user=instance, username=username)
        number = 0
        while True:
            try:
                profile.save()
                return
            except IntegrityError:
                profile.username = username + str(number)
                number += 1
