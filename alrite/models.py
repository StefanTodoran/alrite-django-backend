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
    start_date = models.DateTimeField(blank=True, null=True)
    age = models.CharField(max_length=255, blank=True, null=True)
    age2 = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    weight = models.CharField(max_length=255, blank=True, null=True)
    muac = models.CharField(max_length=255, blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    difficulty_breathing = models.CharField(max_length=255, blank=True, null=True)
    days_with_breathing_difficulties = models.CharField(max_length=255, blank=True, null=True)
    hiv_status = models.CharField(max_length=255, blank=True, null=True)
    child_in_hiv_care = models.CharField(max_length=255, blank=True, null=True)
    temperature = models.CharField(max_length=255,  blank=True, null=True)
    febrile_to_touch = models.CharField(max_length=255,  blank=True, null=True)
    blood_oxygen_saturation = models.CharField(max_length=255, blank=True, null=True)
    respiratory_rate = models.CharField(max_length=255, blank=True, null=True)
    breathing_rate = models.CharField(max_length=255, blank=True, null=True)
    respiratory_rate_score = models.CharField(max_length=255, blank=True, null=True)
    respiratory_rate_2 = models.CharField(max_length=255, blank=True, null=True)
    breathing_rate_2 = models.CharField(max_length=255, blank=True, null=True)
    respiratory_rate_score_2 = models.CharField(max_length=255, blank=True, null=True)
    stridor = models.CharField(max_length=255, blank=True, null=True)
    nasal_flaring = models.CharField(max_length=255, blank=True, null=True)
    wheezing = models.CharField(max_length=255, blank=True, null=True)
    wheezing_2 = models.CharField(max_length=255, blank=True, null=True)
    stethoscope_used = models.CharField(max_length=255, blank=True, null=True)
    chest_indrawing = models.CharField(max_length=255, blank=True, null=True)
    chest_indrawing_2 = models.CharField(max_length=255, blank=True, null=True)
    bronchodilator = models.CharField(max_length=255, blank=True, null=True)
    after_bronchodilator = models.CharField(max_length=255, blank=True, null=True)
    bronchodilator_not_given_reason = models.TextField(blank=True, null=True)
    clinician_diagnosis = models.TextField(blank=True, null=True)
    clinician_treatment = models.TextField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    duration = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_1 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_2 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_3 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_4 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_5 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_6 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_7 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_8 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_9 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_10 = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_11 = models.CharField(max_length=255, blank=True, null=True)
    wheezing_before_this_illness = models.CharField(max_length=255, blank=True, null=True)
    child_breathless = models.CharField(max_length=255, blank=True, null=True)
    breathing_difficulties_last_year = models.CharField(max_length=255, blank=True, null=True)
    child_ever_had_eczema = models.CharField(max_length=255, blank=True, null=True)
    child_parents_with_allergies = models.CharField(max_length=255, blank=True, null=True)
    smoke_tobacco = models.CharField(max_length=255, blank=True, null=True)
    use_kerosene = models.CharField(max_length=255, blank=True, null=True)
    incomplete = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.patient_uuid


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False,  **kwargs):
    if created:
        Token.objects.create(user=instance)