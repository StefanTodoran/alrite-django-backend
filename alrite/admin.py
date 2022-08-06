from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


# Register your models here.
@admin.register(Patient, CustomUser, Health_Facility)
class ViewAdmin(ImportExportModelAdmin):
    pass