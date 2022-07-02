from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Health_Facility(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    healthy_facility = models.ForeignKey(Health_Facility, null=True, blank=True, on_delete=models.SET_NULL)
    is_admin = models.BooleanField(default=False)
    is_nurse = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)

    def __str__(self):
        # return f'{self.first_name} {self.last_name}'
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False,  **kwargs):
    if created:
        Token.objects.create(user=instance)