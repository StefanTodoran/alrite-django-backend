from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


# Create your models here.
# new changes


class Health_Facility(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    healthy_facility = models.ForeignKey(Health_Facility, null=True, blank=True, on_delete=models.SET_NULL)
    forms = models.IntegerField(default=0)
    code = models.CharField(max_length=255, blank=True, null=True)
    completed_forms = models.IntegerField(default=0)
    incomplete_forms = models.IntegerField(default=0)
    is_admin = models.BooleanField(default=False)
    is_nurse = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)

    def __str__(self):
        # return f'{self.first_name} {self.last_name}'
        return self.username

"""
Model that stores a workflow in JSON format, as well
as attributes about the workflow
Workflows are meant to be readonly and rarely modified, the purpose
of the version field is to allow for modifications to
be made without losing the previous workflow
"""
class Workflow(models.Model):
    workflow_id = models.CharField(max_length=63)
    display_name = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    time_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    json = models.TextField() # Using TextField instead of JSONField because we don't need to parse/query the
                              # JSON on the server, also its not well supported on databases

class Counter(models.Model):
    clinician = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL)
    chest_indrawing_count = models.IntegerField(default=0)
    grant_count = models.IntegerField(default=0)
    bronchodilator_count = models.IntegerField(default=0)
    wheezing_count = models.IntegerField(default=0)
    stridor_count = models.IntegerField(default=0)
    nasal_count = models.IntegerField(default=0)
    eczema_count = models.IntegerField(default=0)
    rr_counter_count = models.IntegerField(default=0)
    manual_count = models.IntegerField(default=0)
    learn_opening_count = models.IntegerField(default=0)
    app_opening_count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.clinician.username


class Patient(models.Model):
    clinician = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="form_filler")
    clinician_2 = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL, related_name="logged_in_user")
    patient_uuid = models.CharField(max_length=255)
    app_version = models.IntegerField(default=1)
    study_id = models.CharField(max_length=255, blank=True, null=True)
    patient_initials = models.CharField(max_length=255)
    parent_initials = models.CharField(max_length=255)
    start_date = models.DateTimeField(blank=True, null=True)
    start_date_2 = models.DateTimeField(blank=True, null=True)
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
    end_date_2 = models.DateTimeField(blank=True, null=True)
    duration_2 = models.CharField(max_length=255, blank=True, null=True)
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
        return self.study_id


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False,  **kwargs):
    if created:
        Token.objects.create(user=instance)
