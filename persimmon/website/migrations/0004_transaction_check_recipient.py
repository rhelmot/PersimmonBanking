# Generated by Django 3.1.5 on 2021-03-19 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20210318_0431'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='check_recipient',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
