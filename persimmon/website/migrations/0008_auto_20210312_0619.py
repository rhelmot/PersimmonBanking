# Generated by Django 3.1.5 on 2021-03-12 13:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_appointment_apptime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='apptime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]