from django.db import transaction

from .models import Transaction, ApprovalStatus, EmployeeLevel, User

CRITICAL_THRESHOLD = 1000


def required_approvals(stmt: Transaction):
    """
    Use this function to determine what approvals are necessary for a given transaction

    :param stmt: A Transaction currently pending approval
    :return: A tuple (approval_from_employee, approval_from_user).
             approval_from_employee will be an EmployeeLevel and approval_from_user will be a User indicating who needs
             to give approval. If either field is inapplicable it will contain None.
    """
    # first, check for user approval.
    # if it's a transfer, it needs to be approved by the debtor
    # if it's a credit/debit, it needs to be approved always
    if stmt.is_transfer:
        user_approval = stmt.account_subtract.owner
    else:
        user_approval = stmt.account_only.owner

    # next, check for employee approval
    # if either user is above the critical limit then we need T2
    # if the transaction is a debit/credit then we need T1
    # if this would bankrupt the debtor then we need T1 also
    # otherwise nobody
    user1_volume = stmt.account_add.owner.transaction_volume() + stmt.transaction \
        if stmt.account_add is not None else 0
    user2_volume = stmt.account_subtract.owner.transaction_volume() + stmt.transaction \
        if stmt.account_subtract is not None else 0
    if user1_volume > CRITICAL_THRESHOLD or user2_volume > CRITICAL_THRESHOLD:
        employee_approval = EmployeeLevel.MANAGER
    elif not stmt.is_transfer:
        employee_approval = EmployeeLevel.TELLER
    elif stmt.account_subtract.balance < stmt.transaction:
        employee_approval = EmployeeLevel.TELLER
    else:
        employee_approval = None

    return employee_approval, user_approval


@transaction.atomic
def check_approvals(stmt: Transaction, user: User):
    """
    Check if a user can approve a transaction. As a side effect, if the transaction can be automatically approved,
    it will be.

    :param stmt: The transaction to check
    :param user: Check if this user can approve this transaction
    :return: A bool indicating whether this user can approve this transaction
    """
    # Nobody can approve non-pending transactions
    if stmt.approval_status != ApprovalStatus.PENDING:
        return False

    # check which approvals are needed for this kind of transaction
    employee_approval, user_approval = required_approvals(stmt)

    # for each of the requirements:
    # - if it is None it is not needed. skip.
    # - if it is already satisfied, set the _approval local variable to None
    # - if it is not satisfied and the current user is applicable, return True
    if employee_approval is not None:
        if stmt.transactionapproval_set.filter(approver__employee_level__gte=employee_approval).exists():
            employee_approval = None
        elif user.employee_level >= employee_approval:
            return True
    if user_approval is not None:
        if stmt.transactionapproval_set.filter(approver=user_approval).exists():
            user_approval = None
        elif user_approval == user:
            return True

    # if we get to the end and both requirements have been set to None, the transaction can be automatically approved
    if employee_approval is None and user_approval is None:
        stmt.approve()
    return False


def applicable_approvals(user: User):
    for stmt in Transaction.objects.filter(approval_status=ApprovalStatus.PENDING):
        if check_approvals(stmt, user):
            yield stmt
