from django.db import models


class EmployeeLevel(models.IntegerChoices):
    CUSTOMER = 0
    TELLER = 1
    MANAGER = 2
    ADMIN = 3


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    employee_level = models.IntegerField(choices=EmployeeLevel.choices)

    def check_level(self, level):
        """
        Returns whether user has permission for the given level
        """
        return self.employee_level >= level


class AccountType(models.IntegerChoices):
    CHECKING = 0
    SAVINGS = 1
    CREDIT = 2


class BankAccount(models.Model):
    id = models.IntegerField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(decimal_places=2, max_digits=10)
    type = models.IntegerField(choices=AccountType.choices)

    @property
    def account_number(self):
        return '%016d' % self.id

    def bank_statements(self, start_day, end_day):
        result = BankStatements.objects.filter(bankAccountId=self.id, date__range=[start_day, end_day])
        return result


class BankStatements(models.Model):
    date = models.DateField(auto_now=True)
    transaction = models.CharField(max_length=30)
    balance = models.DecimalField(decimal_places=2,max_digits=10)
    bankAccountId = models.ForeignKey(BankAccount, on_delete=models.CASCADE)


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
