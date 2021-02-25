# Generated by Django 3.1.5 on 2021-02-25 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bankstatements',
            old_name='bankAccountId',
            new_name='accountId',
        ),
        migrations.AddField(
            model_name='bankstatements',
            name='approval_status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Declined')], default=0),
        ),
        migrations.AddField(
            model_name='bankstatements',
            name='description',
            field=models.CharField(default='credit', max_length=20),
        ),
        migrations.AlterField(
            model_name='bankstatements',
            name='balance',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='bankstatements',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='bankstatements',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='bankstatements',
            name='transaction',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
