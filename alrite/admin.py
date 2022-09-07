from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


# Register your models here.
# new changes
@admin.register(Patient, CustomUser, Health_Facility, Counter)
class ViewAdmin(ImportExportModelAdmin):
    pass