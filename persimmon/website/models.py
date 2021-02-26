from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User as DjangoUser  # pylint: disable=imported-auth-user


class ApprovalStatus(models.IntegerChoices):
    PENDING = 0
    APPROVED = 1
    DECLINED = 2


class EmployeeLevel(models.IntegerChoices):
    CUSTOMER = 0
    TELLER = 1
    MANAGER = 2
    ADMIN = 3


class User(models.Model):
    id = models.AutoField(primary_key=True)
    django_user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    employee_level = models.IntegerField(choices=EmployeeLevel.choices)

    @property
    def email(self):
        return self.django_user.email

    @property
    def username(self):
        return self.django_user.username

    @property
    def name(self):
        return '%s %s' % (self.django_user.first_name, self.django_user.last_name)

    def check_level(self, level):
        """
        Returns whether user has permission for the given level
        """
        return self.employee_level >= level

    def change_email(self, new_email):
        self.django_user.email = new_email
        self.django_user.save()
        return self.django_user.email


class AccountType(models.IntegerChoices):
    CHECKING = 0
    SAVINGS = 1
    CREDIT = 2


class BankAccount(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    type = models.IntegerField(choices=AccountType.choices)
    approval_status = models.IntegerField(choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)

    @property
    def account_number(self):
        return '%016d' % self.id


class BankStatements(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    transaction = models.DecimalField(decimal_places=2, max_digits=10)
    balance = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    accountId = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    description = models.CharField(max_length=20, default="credit")
    approval_status = models.IntegerField(choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        if self.date is None:
            self.date = timezone.now()
        super().save(*args, **kwargs)


class SignInHistory(models.Model):
    log = models.DateTimeField(auto_now = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Appointment(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_customer')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_employee',
            limit_choices_to={'employee_level__gte': EmployeeLevel.TELLER})
    time = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'time'], name='employee_availability')
        ]
