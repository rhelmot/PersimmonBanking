from decimal import Decimal

from django.db import models
from django.db.transaction import atomic
from django.utils import timezone
from django.contrib.auth.models import User as DjangoUser  # pylint: disable=imported-auth-user
from django.conf import settings
try:
    from hfc.fabric import Client
    from hfc.fabric_network.gateway import Gateway
except ImportError:
    Client = None
    Gateway = None

from .common import event_loop  # pylint: disable=cyclic-import


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

    def __str__(self):
        return f'{self.name} ({self.id})'

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
                            Transaction.objects.filter(account_add__owner=self)) \
                .filter(approval_status=ApprovalStatus.APPROVED, date__gt=timezone.now() - period):
            acc += abs(transaction.transaction)
        return acc


class UserEditRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    # email = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=200, null=True)

    # phone = models.CharField(max_length=10, null=True)

    def apply(self):
        if self.firstname is not None:
            self.user.django_user.first_name = self.firstname
        if self.lastname is not None:
            self.user.django_user.last_name = self.lastname
        # if self.email is not None:
        #    user.django_user.email = self.email
        if self.address is not None:
            self.user.address = self.address
        # if self.phone is not None:
        #    user.phone = self.phone
        self.user.django_user.save()
        self.user.save()

    def __str__(self):
        changes = []
        if self.firstname is not None or self.lastname is not None:
            changes.append(f'change name to "{self.firstname} {self.lastname}"')
        if self.address is not None:
            changes.append(f'change address to {self.address}')

        return f'{self.user.name}: {" ".join(changes)}'


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
        return f'{self.account_number} ({self.owner.name} {self.pretty_type})'

    def str_with_balance(self):
        return f'{self.account_number} (${self.balance} {self.pretty_type})'

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
    description = models.CharField(max_length=100, default="credit")
    approval_status = models.IntegerField(choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)
    check_recipient = models.CharField(max_length=200, null=True)

    account_add = models.ForeignKey(BankAccount, on_delete=models.CASCADE, null=True, related_name='+')
    account_subtract = models.ForeignKey(BankAccount, on_delete=models.CASCADE, null=True, related_name='+')
    balance_add = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    balance_subtract = models.DecimalField(decimal_places=2, max_digits=10, null=True)

    class Meta:
        constraints = [models.constraints.CheckConstraint(check=models.Q(transaction__gt=0), name='positive_value')]

    def __str__(self):
        pieces = [f'Transaction of ${self.transaction}']
        if self.account_subtract:
            pieces.append(f'from {self.account_subtract.owner.name}')
        if self.account_add:
            pieces.append(f'to {self.account_add.owner.name}')
        return ' '.join(pieces)

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

    @atomic
    def approve(self):
        self2 = Transaction.objects.select_for_update().get(id=self.id)
        if self2.approval_status != ApprovalStatus.PENDING:
            return

        self2.approval_status = ApprovalStatus.APPROVED
        self2.date = timezone.now()

        if self2.account_add is not None:
            account_add = BankAccount.objects.select_for_update().get(id=self2.account_add.id)
            account_add.balance += self2.transaction
            account_add.save()
            self2.balance_add = account_add.balance
            date = self2.date.strftime("%m/%d/%Y, %H:%M:%S")
            self.create_bank_statement_to_blockchain(self2.id, date, self2.transaction, account_add.balance,
                                                     account_add.id, self2.description)
        if self2.account_subtract is not None:
            account_sub = BankAccount.objects.select_for_update().get(id=self2.account_subtract.id)
            account_sub.balance -= self2.transaction
            account_sub.save()
            self2.balance_subtract = account_sub.balance
            date = self2.date.strftime("%m/%d/%Y, %H:%M:%S")
            self.create_bank_statement_to_blockchain(self2.id, date, self2.transaction, account_sub.balance,
                                                     account_sub.id, self2.description)
        self2.save()

    def decline(self):
        if self.approval_status != ApprovalStatus.PENDING:
            return
        self.approval_status = ApprovalStatus.DECLINED
        self.date = timezone.now()
        self.save()

    def for_one_account(self, account):
        # subtract first because subtract is second during approval
        if self.account_subtract == account:
            # pylint: disable=invalid-unary-operand-type
            return BankStatementEntry(
                self.id,
                self.date,
                -self.transaction,
                self.balance_subtract,
                self.description,
                self.check_recipient)
        if self.account_add == account:
            return BankStatementEntry(
                self.id,
                self.date,
                self.transaction,
                self.balance_add,
                self.description,
                self.check_recipient)
        raise Exception("Called for_one_account with account not associated with transaction")

    @staticmethod
    def create_bank_statement_to_blockchain(transaction_id: int, date: str, new_transaction: Decimal,
                                            balance: Decimal, account_id: int, description: str):
        if not settings.BLOCKCHAIN_CONNECTION:
            return

        loop = event_loop()
        cli = Client(net_profile=settings.BLOCKCHAIN_CONNECTION)
        org1_admin = cli.get_user(org_name='Org1', name='Admin')
        new_gateway = Gateway()  # Creates a new gateway instance
        options = {'wallet': ''}
        loop.run_until_complete(new_gateway.connect(settings.BLOCKCHAIN_CONNECTION, options))
        new_network = loop.run_until_complete(new_gateway.get_network('mychannel', org1_admin))
        new_contract = new_network.get_contract('bankcode')
        cli = new_gateway.client
        transaction_id = str(transaction_id)
        new_transaction = str(new_transaction)
        balance = str(balance)
        account_id = str(account_id)
        args = [transaction_id, date, new_transaction, balance, account_id, description, "approved"]

        response = cli.chaincode_invoke(requestor=org1_admin,
                                        channel_name=new_contract.network.channel.name,
                                        peers=cli._peers,  # pylint: disable=protected-access
                                        args=args,
                                        cc_name=new_contract.cc_name,
                                        wait_for_event=True,
                                        fcn="createBankStatement")
        loop.run_until_complete(response)


class BankStatementEntry:
    """
    Small data class to contain a slice of a Transaction related to a single account. use Transaction.for_one_account
    to get one of these.
    """

    def __init__(self, ident, date, transaction, balance, description, check_recipient):
        self.id = ident  # pylint: disable=invalid-name
        self.date = date
        self.transaction = transaction
        self.balance = balance
        self.description = description
        self.check_recipient = check_recipient
        self.can_approve = False


class TransactionApproval(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="+")
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    timestamp = models.DateTimeField(auto_now=True)


class SignInHistory(models.Model):
    log = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} - {self.log}'

    class Meta:
        verbose_name_plural = 'Sign In Histories'


class SignInFailure(models.Model):
    log = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=50)
    info = models.CharField(max_length=1000)

    def __str__(self):
        return f'{self.ip} - {self.log} ({self.info})'

    @classmethod
    def locked_out(cls, ip_addr, attempts=6, cooldown=timezone.timedelta(days=1)):
        return cls.objects.filter(ip=ip_addr, log__gt=timezone.now() - cooldown).count() >= attempts


class Appointment(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_customer')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_employee',
                                 limit_choices_to={'employee_level__gte': EmployeeLevel.TELLER})
    time = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'time'], name='employee_availability')
        ]
