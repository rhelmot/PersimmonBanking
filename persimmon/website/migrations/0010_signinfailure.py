# Generated by Django 3.1.5 on 2021-04-03 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_auto_20210402_2351'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignInFailure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.DateTimeField(auto_now=True)),
                ('ip', models.CharField(max_length=50)),
                ('info', models.CharField(max_length=1000)),
            ],
        ),
    ]
