from website.models import DjangoUser, EmployeeLevel, ApprovalStatus, AccountType, BankAccount, BankStatements, \
    SignInHistory, Appointment, User

def run():
    django_user = DjangoUser.objects.create_user(
        username="GauravDeshpande",
        first_name="Gaurav",
        last_name="Deshpande",
        email="gaurav@email.com",
        password="gauravspassword")
    User.objects.create(
        phone="4809993456",
        address="address",
        employee_level=EmployeeLevel.CUSTOMER,
        django_user=django_user)
