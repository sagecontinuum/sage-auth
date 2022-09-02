from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Token(models.Model):
    user = models.CharField(max_length=50)
    tokenValue = models.CharField(max_length=20)
    expires = models.DateTimeField()
    scope = models.TextField(default='default')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sage_username = models.CharField(max_length=15)
    bio = models.TextField(max_length=500, blank=True)
    organization = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return '{}; {}'.format(self.user, self.sage_username)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        Profile.objects.create(user=user)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

