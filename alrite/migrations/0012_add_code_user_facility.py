# Generated by Django 4.1.7 on 2023-04-23 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alrite', '0011_pending_changes_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='health_facility',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
