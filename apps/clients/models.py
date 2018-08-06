from django.db import models
from django.conf import settings


class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(u"Full Name", null=True, blank=True, max_length=255)
    favourite_colour = models.CharField(u"Favorite Color", null=True, blank=True, max_length=255)

    def __str__(self):
        return self.user.email