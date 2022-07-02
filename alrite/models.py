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


class Patient(models.Model):
    clinician = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL)
    patient_uuid = models.CharField(max_length=255)
    patient_initials = models.CharField(max_length=255)
    parent_initials = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    age = models.CharField(max_length=255)
    weight = models.CharField(max_length=255)
    muac = models.CharField(max_length=255, blank=True, null=True)
    symptoms = models.TextField()
    difficulty_breathing = models.CharField(max_length=255)
    days_with_breathing_difficulties = models.CharField(max_length=255)
    hiv_status = models.CharField(max_length=255)
    in_hiv_care = models.CharField(max_length=255, blank=True, null=True)
    temperature = models.CharField(max_length=255,  blank=True, null=True)
    febrile_to_touch = models.CharField(max_length=255,  blank=True, null=True)
    blood_oxygen_saturation = models.CharField(max_length=255, blank=True, null=True)
    respiratory_rate = models.CharField(max_length=255)
    breathing_rate = models.CharField(max_length=255)
    respiratory_rate_score = models.CharField(max_length=255)
    stridor = models.CharField(max_length=255)
    nasal_flaring = models.CharField(max_length=255)
    wheezing = models.CharField(max_length=255)
    indrawing = models.CharField(max_length=255)
    bronchodilator = models.CharField(max_length=255)
    bronchodilator_not_given_reason = models.TextField(blank=True, null=True)
    clinician_diagnosis = models.TextField()
    clinician_treatment = models.TextField()
    start_date = models.DateTimeField()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False,  **kwargs):
    if created:
        Token.objects.create(user=instance)