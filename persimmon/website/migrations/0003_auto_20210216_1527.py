# Generated by Django 3.1.5 on 2021-02-16 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_bankstatements_approval_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bankstatements',
            old_name='bankAccountId',
            new_name='accountId',
        ),
        migrations.AlterField(
            model_name='bankstatements',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]