# Generated by Django 3.1.5 on 2021-02-04 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20210204_0136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
