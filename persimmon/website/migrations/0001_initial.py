
# Generated by Django 3.1.5 on 2021-03-13 22:19


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('type', models.IntegerField(choices=[(0, 'Checking'), (1, 'Savings'), (2, 'Credit')])),
                ('approval_status', models.IntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Declined')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('transaction', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(default='credit', max_length=20)),
                ('approval_status', models.IntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Declined')], default=0)),
                ('balance_add', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('balance_subtract', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('account_add', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='website.bankaccount')),
                ('account_subtract', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='website.bankaccount')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('phone', models.CharField(max_length=10)),
                ('address', models.CharField(max_length=200)),
                ('employee_level', models.IntegerField(choices=[(0, 'Customer'), (1, 'Teller'), (2, 'Manager'), (3, 'Admin')])),
                ('django_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionApproval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='website.user')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='SignInHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.user')),
            ],
        ),
        migrations.AddField(
            model_name='bankaccount',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.user'),
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments_as_customer', to='website.user')),
                ('employee', models.ForeignKey(limit_choices_to={'employee_level__gte': 1}, on_delete=django.db.models.deletion.CASCADE, related_name='appointments_as_employee', to='website.user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='transaction',
            constraint=models.CheckConstraint(check=models.Q(transaction__gt=0), name='positive_value'),
        ),
        migrations.AddConstraint(
            model_name='appointment',
            constraint=models.UniqueConstraint(fields=('employee', 'time'), name='employee_availability'),
        ),
    ]
