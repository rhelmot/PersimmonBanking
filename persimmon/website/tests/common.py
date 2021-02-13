from ..models import User, DjangoUser, EmployeeLevel
from .. views import create_user_account


create_user_account(request, username,
              first_name='Firstname',
              last_name='Lastname',
              password='password',
              email='example@example.com',
              phone='0000000000',
              address='nowhere',
              employee_level=EmployeeLevel.CUSTOMER)

