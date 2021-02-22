# Generated by Django 3.1.5 on 2021-02-10 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankstatements',
            name='approval_status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Declined')], default=0),
        ),
    ]
