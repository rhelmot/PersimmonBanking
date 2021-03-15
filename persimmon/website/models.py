from django.contrib.auth.models import User as DjangoUser  # pylint: disable=imported-auth-user
from django.db import models
from django.utils import timezone


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
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'<User {self.name}>'

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

    def transaction_volume(self, period=timezone.timedelta(days=1)):
        acc = 0
        for transaction in (Transaction.objects.filter(account_subtract__owner=self) |
                            Transaction.objects.filter(account_add__owner=self))\
                .filter(approval_status=ApprovalStatus.APPROVED, date__gt=timezone.now() - period):
            acc += abs(transaction.transaction)
        return acc


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

    def __str__(self):
        return f'<BankAccount {self.id} ({self.owner.name})>'

    @property
    def account_number(self):
        return '%016d' % self.id

    @property
    def pretty_type(self):
        if self.type == AccountType.CHECKING:
            return "Checking"
        if self.type == AccountType.SAVINGS:
            return "Savings"
        if self.type == AccountType.CREDIT:
            return "Credit"
        raise ValueError("This should be unreachable")

    @property
    def transactions(self):
        return Transaction.objects.filter(account_add=self) | Transaction.objects.filter(account_subtract=self)


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=timezone.now)
    transaction = models.DecimalField(decimal_places=2, max_digits=10, )
    description = models.CharField(max_length=20, default="credit")
    approval_status = models.IntegerField(choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)

    account_add = models.ForeignKey(BankAccount, on_delete=models.CASCADE, null=True, related_name='+')
    account_subtract = models.ForeignKey(BankAccount, on_delete=models.CASCADE, null=True, related_name='+')
    balance_add = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    balance_subtract = models.DecimalField(decimal_places=2, max_digits=10, null=True)

    class Meta:
        constraints = [models.constraints.CheckConstraint(check=models.Q(transaction__gt=0), name='positive_value')]

    def __str__(self):
        return f'<Transaction "{self.description}" ${self.transaction}>'

    @property
    def is_transfer(self):
        return self.account_add is not None and self.account_subtract is not None

    @property
    def account_only(self):
        if self.is_transfer:
            raise Exception("Cannot call account_only on a transfer transaction")
        return self.account_add if self.account_add is not None else self.account_subtract

    def add_approval(self, user):
        TransactionApproval.objects.create(approver=user, transaction=self)

    def approve(self):
        if self.approval_status != ApprovalStatus.PENDING:
            return

        self.approval_status = ApprovalStatus.APPROVED
        self.date = timezone.now()

        if self.account_add is not None:
            self.account_add.balance += self.transaction
            self.balance_add = self.account_add.balance
            self.account_add.save()
        if self.account_subtract is not None:
            self.account_subtract.balance -= self.transaction
            self.balance_subtract = self.account_subtract.balance
            self.account_subtract.save()

        self.save()

    def decline(self):
        if self.approval_status != ApprovalStatus.PENDING:
            return
        self.approval_status = ApprovalStatus.DECLINED
        self.date = timezone.now()
        self.save()

    def for_one_account(self, account):
        if self.account_add == account:
            return BankStatementEntry(self.id, self.date, self.transaction, self.balance_add, self.description)
        if self.account_subtract == account:
            return BankStatementEntry(self.id, self.date, -self.transaction, self.balance_add, self.description)
        raise Exception("Called for_one_account with account not associated with transaction")


class BankStatementEntry:
    """
    Small data class to contain a slice of a Transaction related to a single account. use Transaction.for_one_account
    to get one of these.
    """
    def __init__(self, ident, date, transaction, balance, description):
        self.id = ident
        self.date = date
        self.transaction = transaction
        self.balance = balance
        self.description = description
        self.can_approve = False


class TransactionApproval(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    timestamp = models.DateTimeField(auto_now=True)


class SignInHistory(models.Model):
    log = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Appointment(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_customer')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_employee',
                                 limit_choices_to={'employee_level__gte': EmployeeLevel.TELLER})
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'time'], name='employee_availability')
        ]
