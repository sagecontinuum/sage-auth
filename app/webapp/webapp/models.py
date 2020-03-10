from django.db import models

class Token(models.Model):
    user = models.CharField(max_length=20)
    tokenValue = models.CharField(max_length=20)
    expires = models.DateTimeField()
    scope = models.TextField(default='default')

