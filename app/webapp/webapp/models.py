from django.db import models

class Token(models.Model):
    user = models.CharField(max_length=20)
    tokenValue = models.CharField(max_length=20)
    expires = models.DateTimeField()


# draft of system to assign different permnissions (scopes) to tokens
class TokenScopes:
    tokenValue = models.CharField(max_length=20)
    scope = models.CharField(max_length=10)
