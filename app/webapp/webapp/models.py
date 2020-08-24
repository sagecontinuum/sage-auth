from django.db import models

class Token(models.Model):
    user = models.CharField(max_length=50)
    tokenValue = models.CharField(max_length=20)
    expires = models.DateTimeField()
    scope = models.TextField(default='default')

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from prometheus_client import Counter, start_http_server

login_counter = Counter("login_counter", "This metric counts the total number of logins")


@receiver(user_logged_in)
def update_user_login(sender, **kwargs): # Receiver function
    kwargs.pop('user', None)
    login_counter.inc(1)

# user_logged_in.connect(update_user_login, sender=User)


