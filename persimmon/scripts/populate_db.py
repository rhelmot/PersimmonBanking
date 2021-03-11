from website.models import DjangoUser, User, EmployeeLevel

def run():
    django_user1 = DjangoUser.objects.create_user(
        username="GauravDeshpande",
        first_name="Gaurav",
        last_name="Deshpande",
        email="gaurav@email.com",
        password="gauravspassword")
    User.objects.create(
        phone="4809993456",
        address="address",
        employee_level=EmployeeLevel.CUSTOMER,
        django_user=django_user1)

    django_user2 = DjangoUser.objects.create_user(
        username="BobMeyers",
        first_name="Bob",
        last_name="Meyers",
        email="bob@email.com",
        password="bobspassword")
    User.objects.create(
        phone="3456923456",
        address="address",
        employee_level=EmployeeLevel.CUSTOMER,
        django_user=django_user2)

    django_user3 = DjangoUser.objects.create_user(
        username="JoeSanders",
        first_name="Joe",
        last_name="Sanders",
        email="joe@email.com",
        password="joespassword")
    User.objects.create(
        phone="6025679435",
        address="address",
        employee_level=EmployeeLevel.CUSTOMER,
        django_user=django_user3)

    django_user4 = DjangoUser.objects.create_user(
        username="AudreyDutcher",
        first_name="Audrey",
        last_name="Dutcher",
        email="audrey@email.com",
        password="audreypassword")
    User.objects.create(
        phone="4803831341",
        address="address",
        employee_level=EmployeeLevel.TELLER,
        django_user=django_user4)

    django_user5 = DjangoUser.objects.create_user(
        username="AkshayKoshy",
        first_name="Akshay",
        last_name="Koshy",
        email="akshay@email.com",
        password="akshaypassword")
    User.objects.create(
        phone="4802315314",
        address="address",
        employee_level=EmployeeLevel.MANAGER,
        django_user=django_user5)

    django_user6 = DjangoUser.objects.create_user(
        username="RunlinXiao",
        first_name="Runlin",
        last_name="Xiao",
        email="runlin@email.com",
        password="runlinpassword")
    User.objects.create(
        phone="3452987645",
        address="address",
        employee_level=EmployeeLevel.MANAGER,
        django_user=django_user6)

    django_user7 = DjangoUser.objects.create_user(
        username="BrennanLannone",
        first_name="Brennan",
        last_name="Lannone",
        email="brennan@email.com",
        password="brennanpassword")
    User.objects.create(
        phone="3560987869",
        address="address",
        employee_level=EmployeeLevel.ADMIN,
        django_user=django_user7)
