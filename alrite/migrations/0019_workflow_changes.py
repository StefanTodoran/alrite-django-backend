# Generated by Django 4.1.7 on 2023-05-31 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alrite', '0018_alter_workflow_workflow_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='changes',
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
    ]