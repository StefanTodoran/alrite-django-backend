# Generated by Django 4.1.7 on 2023-04-23 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alrite', '0013_added_workflow_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workflow',
            name='display_name',
        ),
    ]
