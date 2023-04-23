# Generated by Django 4.1.7 on 2023-04-23 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alrite', '0010_patient_study_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='counter',
            name='manual_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='patient',
            name='app_version',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='counter',
            name='app_opening_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='bronchodilator_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='chest_indrawing_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='eczema_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='grant_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='learn_opening_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='nasal_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='rr_counter_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='stridor_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='counter',
            name='wheezing_count',
            field=models.IntegerField(default=0),
        ),
    ]
