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

    # placeholder till website itself is up
    def chk_address(self):
        for char in self.address:
            if char in "!/?!.:;|":
                print("invalid input cannot have /?!.:;|")
                break

    def change_phone_number(self):
        t = 0
        while (t == 0):
            self.phone = input("enter here")
            if len(self.phone) > 10:
                print("invalid")
            else:
                for char in self.phone:
                    if char in "0123456789":
                        t = 1
                        continue
                    else:
                        print("invalid input")
                        t = 0
                        break





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

class SignInHistory(models.Model):
    log = models.DateTimeField(auto_now = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)