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
    employee_level = models.IntegerField(choices=EmployeeLevel.choices)

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

class BankStatements(models.Model):
    date = models.DateField(auto_now=True)
    debit = models.DecimalField(decimal_places=2, max_length=10,null=True)
    credit = models.DecimalField(decimal_places=2,max_length=10,null=True)
    balance = models.DecimalField(decimal_places=2,max_length=10)
    bankAccount = models.ForeignKey(BankAccount, on_delete=models.CASCADE)